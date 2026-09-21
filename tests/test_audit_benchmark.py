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


PDF_PATH = Path("data/documents/sample_contract.pdf")


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
    summary = extractor.extract([])

    assert len(summary.provider_obligations) >= 5
    assert len(summary.customer_obligations) >= 3
    assert len(summary.timeline) >= 10

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
    assert "recover" in f_deal["plain_english"].lower()

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
    gb = GraphBuilder()
    graph = gb.build(
        findings=[{
            "title": "15-Day Unilateral Termination",
            "category": "termination",
            "severity": "critical",
            "bucket": "deal_breaker",
            "evidence": [{"chunk_id": "chunk-0012", "page": 3, "quote": "15 days written notice"}],
        }],
        parties={"customer": "Northstar", "provider": "Meridian"}
    )
    serialized = gb.serialize(graph)

    assert serialized["total_nodes"] >= 15
    assert serialized["total_links"] >= 12

    # Check that core relationships have quotes and page numbers
    for link in serialized["links"]:
        if link["relationship"] in {"TERMINATES_CONVENIENCE", "RETAINS_BACKUP", "MAY_AUDIT", "COMMITS_SLA"}:
            assert link["page_number"] is not None
            assert len(link["quote"]) > 0
