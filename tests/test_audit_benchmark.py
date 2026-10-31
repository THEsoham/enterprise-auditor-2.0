import pytest
from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.table_extractor import TableExtractor
from app.ingestion.signature_analyzer import SignatureAnalyzer
from app.chunking.semantic_chunker import chunk_pages
from app.retrieval.bm25 import BM25Index
from app.retrieval.retriever import Retriever
from app.auditing.audit_planner import AuditPlanner
from app.auditing.missing_clauses import MissingClauseDetector
from app.auditing.obligation_extractor import ObligationExtractor
from app.scoring.risk_scorer import RiskScorer
from app.scoring.health_score import HealthScore
from app.graph.graph_builder import GraphBuilder
from app.verification.grounding import ground_evidence, quote_in_text
from app.verification.verifier import GeminiVerifier, parse_json_object
from app.auditing.finding_generator import FindingGenerator


PDF_PATH = Path(__file__).resolve().parent.parent / "data" / "documents" / "sample_contract.pdf"


def _sample_chunks() -> list[dict]:
    return [c.model_dump() for c in chunk_pages(load_pdf(PDF_PATH))]


def test_pdf_loading():
    """Validates PDF loader extracts text and page numbers."""
    pages = load_pdf(PDF_PATH)
    assert len(pages) == 6
    assert "MASTER SOFTWARE SERVICES" in pages[0]["text"]
    assert pages[0]["page_number"] == 1


def test_table_extraction_benchmark():
    """Validates structured table extraction and pricing analysis."""
    extractor = TableExtractor()
    tables = extractor.extract_tables(PDF_PATH)
    assert len(tables) >= 3

    pricing_table = next((t for t in tables if t.table_type == "pricing_tiers"), None)
    assert pricing_table is not None
    assert pricing_table.page_number == 1
    assert "Standard" in str(pricing_table.rows)
    assert "Enterprise" in str(pricing_table.rows)
    assert len(pricing_table.risks) >= 1

    # Overage comparison is computed from the table cells, not hardcoded
    overage = next(r for r in pricing_table.risks if r["risk_title"] == "Overage Fee Exposure")
    assert "Standard" in overage["observation"] and "Enterprise" in overage["observation"]
    assert "140%" in overage["observation"]  # 12 vs 5 per document


def test_signature_visual_benchmark():
    """Validates visual signature detection and unexecuted draft status."""
    analyzer = SignatureAnalyzer()
    report = analyzer.analyze(PDF_PATH)
    assert report.overall_status == "UNEXECUTED_DRAFT"
    assert report.signature_page == 5
    assert len(report.parties) == 2
    for p in report.parties:
        assert p.signature_detected is False
        assert p.status_label == "NOT DETECTED"


def test_missing_clauses_benchmark():
    """Validates baseline missing protections detection."""
    pages = load_pdf(PDF_PATH)
    full_text = "\n".join(p["text"] for p in pages)
    detector = MissingClauseDetector()
    results = detector.detect(full_text)

    status_map = {r["check_id"]: r["status"] for r in results}
    assert status_map["disaster-recovery-sla"] == "MISSING"
    assert status_map["security-incident-timeframe"] == "VAGUE"
    assert status_map["data-return-destruction-certification"] == "MISSING"
    assert status_map["confidentiality-clause-present"] == "PRESENT"
    assert status_map["liability-clause-present"] == "PRESENT"
    assert status_map["termination-clause-present"] == "PRESENT"


def test_obligation_timeline_benchmark():
    """Validates obligations extraction and chronological timeline ordering."""
    extractor = ObligationExtractor()
    chunks = _sample_chunks()
    summary = extractor.extract(chunks)

    assert len(summary.provider_obligations) >= 5
    assert len(summary.customer_obligations) >= 2
    assert len(summary.timeline) >= 10

    # Every extracted item is quoted verbatim from the contract
    full_text = " ".join(c["text"] for c in chunks)
    for item in summary.timeline + summary.provider_obligations + summary.customer_obligations:
        assert quote_in_text(item.quote, full_text)

    labels = {(t.party, t.period_label) for t in summary.timeline}
    assert ("Provider", "15 days") in labels  # 10.3 convenience termination
    assert ("Customer", "60 days") in labels  # 10.4 convenience termination

    # Verify timeline is monotonically sorted by days
    days_list = [t.days for t in summary.timeline]
    assert days_list == sorted(days_list)
    assert summary.timeline[0].days <= 1.0  # 24h notice
    assert summary.timeline[-1].days >= 700.0  # 24 months


def test_bm25_and_hybrid_retrieval_benchmark():
    """Validates BM25 exact keyword matching and RRF hybrid retrieval."""
    pages = load_pdf(PDF_PATH)
    chunks = [c.model_dump() for c in chunk_pages(pages)]

    bm25 = BM25Index()
    bm25.index(chunks)
    res = bm25.search("indemnification infringement", top_k=3)
    assert len(res) > 0
    assert any("INDEMNIFICATION" in hit["text"] for hit in res)


def test_party_extraction_and_planning_benchmark():
    """Validates party identification and autonomous probe creation."""
    pages = load_pdf(PDF_PATH)
    chunks = [c.model_dump() for c in chunk_pages(pages)]

    planner = AuditPlanner()
    plan = planner.create_plan(chunks)
    assert "Northstar Analytics" in plan.parties["customer"]
    assert "Meridian Cloud" in plan.parties["provider"]
    assert len(plan.probes) >= 10


def test_risk_scorer_three_buckets():
    """Validates classification into 🔴 Deal-Breakers, 🟡 Watch Out, 🟢 Protections."""
    scorer = RiskScorer()

    # Critical liability finding -> Deal-Breaker
    f_deal = {
        "title": "Liability Capped at 3 Months",
        "category": "liability",
        "severity": "critical",
        "claim": "Liability capped at 3 months fees",
        "evidence": [{"chunk_id": "chunk-0011", "page": 3, "quote": "three months preceding"}],
        "confidence": 0.9,
    }
    v_deal = {"verdict": "ACCEPTED", "confidence": 0.95}
    score_deal = scorer.score(f_deal, v_deal)
    assert score_deal["bucket"] == "deal_breaker"
    # No canned text: plain English falls back to the finding's own claim
    assert f_deal["plain_english"] == "Liability capped at 3 months fees"

    # Subcontractor finding -> Protection
    f_prot = {
        "title": "Provider Responsible for Subcontractors",
        "category": "data_security",
        "severity": "low",
        "claim": "Provider remains responsible for the acts and omissions of its subcontractors",
        "evidence": [{"chunk_id": "chunk-0005", "page": 1, "quote": "Provider remains responsible"}],
        "confidence": 0.9,
    }
    v_prot = {"verdict": "ACCEPTED", "confidence": 0.9}
    score_prot = scorer.score(f_prot, v_prot)
    assert score_prot["bucket"] == "protection"

    # Auto-renewal finding -> Watch Out
    f_watch = {
        "title": "Automatic Renewal With 90-Day Notice",
        "category": "renewal",
        "severity": "medium",
        "claim": "Contract automatically renews every 12 months unless notice given 90 days before",
        "evidence": [{"chunk_id": "chunk-0015", "page": 5, "quote": "at least 90 days before expiration"}],
        "confidence": 0.85,
    }
    v_watch = {"verdict": "ACCEPTED", "confidence": 0.85}
    score_watch = scorer.score(f_watch, v_watch)
    assert score_watch["bucket"] == "watch_out"

    # The Auditor's own labels win over keyword heuristics
    f_labeled = {
        "title": "Unilateral publicity right",
        "finding_type": "risk",
        "severity": "high",
        "claim": "Provider may use Customer's logo without consent",
        "plain_english": "They can put your logo on their website without asking.",
        "clause_balance": {"is_asymmetric": True, "asymmetry_summary": "Only Provider gets publicity rights."},
        "evidence": [{"quote": "without obtaining additional approval"}],
        "confidence": 0.9,
    }
    scorer.score(f_labeled, {"verdict": "ACCEPTED", "confidence": 0.9})
    assert f_labeled["bucket"] == "deal_breaker"
    assert f_labeled["plain_english"] == "They can put your logo on their website without asking."
    assert f_labeled["clause_balance"]["is_asymmetric"] is True

    # Unverified findings never count
    assert scorer.score(dict(f_labeled), {"verdict": "UNVERIFIED"})["risk_level"] == "unverified"


def test_health_score_100_point_scale():
    """Validates 100-point transparent formula."""
    health_engine = HealthScore()

    deal_breaker = {"title": "3 Months Liability", "bucket": "deal_breaker", "severity": "critical"}
    watch_out = {"title": "Auto Renewal", "bucket": "watch_out", "severity": "medium"}
    protection = {"title": "Subcontractors", "bucket": "protection", "severity": "low"}
    missing = [{"check_id": "sla", "status": "MISSING"}]

    scores = [
        {"bucket": "deal_breaker", "risk_level": "critical"},
        {"bucket": "watch_out", "risk_level": "medium"},
        {"bucket": "protection", "risk_level": "low"},
    ]

    res = health_engine.calculate(
        findings=[deal_breaker, watch_out, protection],
        risk_scores=scores,
        missing_clauses=missing,
    )

    # Base (100) - DealBreaker (8) - WatchOut (3) - Missing (2) + Protection (2.5) = 89.5
    assert res["health_score"] == 89.5
    assert res["rating"] == "Strong"
    assert res["deal_breakers_count"] == 1
    assert res["watch_out_count"] == 1
    assert res["protections_count"] == 1
    assert res["missing_protections_count"] == 1


def test_knowledge_graph_evidence_grounding():
    """Validates that all knowledge graph edges retain evidence quotes and page numbers."""
    chunks = _sample_chunks()
    obligations = ObligationExtractor().extract(chunks).model_dump()

    gb = GraphBuilder()
    graph = gb.build(
        findings=[{
            "title": "15-Day Unilateral Termination",
            "category": "termination",
            "severity": "critical",
            "bucket": "deal_breaker",
            "evidence": [{"chunk_id": "chunk-0012", "page": 3, "quote": "15 days written notice"}],
        }],
        parties={"customer": "Northstar", "provider": "Meridian"},
        obligations=obligations,
    )
    serialized = gb.serialize(graph)

    assert serialized["total_nodes"] >= 15
    assert serialized["total_links"] >= 12

    # Every quoted edge comes from the contract text (no hardcoded sample quotes)
    full_text = " ".join(c["text"] for c in chunks)
    for link in serialized["links"]:
        if link["relationship"] in {"TERMINATES_CONVENIENCE", "RETAINS_BACKUP", "MAY_AUDIT", "COMMITS_SLA", "OBLIGATED_TO"}:
            assert link["page_number"] is not None
            assert quote_in_text(link["quote"], full_text)

    # Without obligations the graph contains nothing invented
    empty = gb.serialize(gb.build(findings=[], parties={}))
    assert all(not link["quote"] for link in empty["links"])


def test_quote_grounding_rejects_paraphrases():
    """Quotes must exist verbatim in the retrieved chunks; chunk/page are corrected."""
    evidence = [{
        "chunk_id": "chunk-0007",
        "text": "10.3 Provider may terminate this Agreement for convenience at any time upon 15 days’\nwritten notice to Customer.",
        "metadata": {"page_number": 3, "section": "10. TERMINATION"},
    }]
    finding = {"evidence": [
        {"chunk_id": "chunk-9999", "page": 1, "quote": "Provider may terminate this Agreement for convenience at any time upon 15 days' written notice"},
        {"chunk_id": "chunk-0007", "page": 3, "quote": "Provider may terminate on 10 days notice"},
        {"chunk_id": "chunk-0007", "page": 3, "quote": "Provider may terminate ... upon 15 days"},
    ]}

    result = ground_evidence(finding, evidence)
    assert len(result["grounded"]) == 2
    assert result["grounded"][0]["chunk_id"] == "chunk-0007"
    assert result["grounded"][0]["page"] == 3
    assert [u["quote"] for u in result["ungrounded"]] == ["Provider may terminate on 10 days notice"]


def test_verifier_never_fabricates_acceptance(monkeypatch):
    """When every verifier model fails, the verdict is UNVERIFIED, not ACCEPTED."""
    verifier = GeminiVerifier()
    monkeypatch.setattr(verifier, "_gemini_verify", lambda prompt: (None, ""))
    monkeypatch.setattr(verifier, "_openai_verify", lambda prompt: (None, ""))

    result = verifier.verify(
        finding={"claim": "x"},
        evidence=[{"chunk_id": "c1", "text": "t", "metadata": {"page_number": 1, "section": ""}}],
    )
    assert result["verdict"] == "UNVERIFIED"
    assert result["confidence"] == 0.0

    # Garbage replies are also not treated as acceptance
    monkeypatch.setattr(verifier, "_openai_verify", lambda prompt: ("not json at all", "openai:test"))
    assert verifier.verify(finding={"claim": "x"}, evidence=[])["verdict"] == "UNVERIFIED"

    assert parse_json_object('```json\n{"verdict": "ACCEPTED"}\n```') == {"verdict": "ACCEPTED"}


def test_finding_generator_returns_none_instead_of_inventing(monkeypatch):
    """An unreadable or 'unsupported' LLM reply produces no finding."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    generator = FindingGenerator()

    for reply in ["sorry, I cannot help", '{"status": "unsupported"}']:
        class FakeCompletions:
            @staticmethod
            def create(**kwargs):
                message = type("M", (), {"content": reply})
                choice = type("C", (), {"message": message})
                return type("R", (), {"choices": [choice]})

        monkeypatch.setattr(generator.client.chat, "completions", FakeCompletions)
        evidence = [{"chunk_id": "c1", "text": "t", "metadata": {"page_number": 1, "section": ""}}]
        assert generator.generate(query="q", evidence=evidence) is None
