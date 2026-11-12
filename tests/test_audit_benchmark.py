import pytest
import pymupdf
from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.table_extractor import TableExtractor
from app.ingestion.signature_analyzer import SignatureAnalyzer
from app.chunking.semantic_chunker import chunk_pages, split_large_text
from app.retrieval.bm25 import BM25Index
from app.retrieval.retriever import Retriever, expand_query
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


def _signed_pdf(path, customer_ink=None, provider_ink=None, logo=False):
    """A one-page contract signature block with optional ink for each party."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 60), "IN WITNESS WHEREOF, the Parties have signed.")
    page.insert_text((72, 120), "For Acme Retail Inc.")
    page.insert_text((72, 140), f"Signature: {customer_ink if customer_ink else '__________'}")
    page.insert_text((72, 320), "For Zenith Cloud LLC")
    page.insert_text((72, 340), f"Signature: {provider_ink if provider_ink else '__________'}")
    if logo:
        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8))
        pixmap.clear_with(120)
        page.insert_image(pymupdf.Rect(400, 20, 440, 50), pixmap=pixmap)
    doc.save(path)
    doc.close()
    return path


def test_signature_checks_each_party_separately(tmp_path):
    """One party can sign without the other, and a page logo is not a signature."""
    analyzer = SignatureAnalyzer()
    parties = {"customer": "Acme Retail Inc.", "provider": "Zenith Cloud LLC"}

    partial = analyzer.analyze(_signed_pdf(tmp_path / "a.pdf", provider_ink="/s/ Jane Doe"), parties=parties)
    assert partial.overall_status == "PARTIALLY_EXECUTED"
    status = {p.party_role: p.signature_detected for p in partial.parties}
    assert status == {"Customer": False, "Provider": True}

    full = analyzer.analyze(_signed_pdf(tmp_path / "b.pdf", "/s/ Ann Lee", "/s/ Jane Doe"), parties=parties)
    assert full.overall_status == "FULLY_EXECUTED"

    logo_only = analyzer.analyze(_signed_pdf(tmp_path / "c.pdf", logo=True), parties=parties)
    assert logo_only.overall_status == "UNEXECUTED_DRAFT"

    # Roles come from the party names, not from which block is first on the page
    swapped = analyzer.analyze(tmp_path / "a.pdf", parties={"customer": "Zenith Cloud LLC", "provider": "Acme Retail Inc."})
    assert {p.party_name: p.party_role for p in swapped.parties} == {"Acme Retail Inc.": "Provider", "Zenith Cloud LLC": "Customer"}


def test_signature_detects_hand_drawn_ink(tmp_path):
    """A signature drawn as curves counts; straight lines do not."""
    path = _signed_pdf(tmp_path / "ink.pdf")
    doc = pymupdf.open(path)
    page = doc[0]
    page.draw_bezier((80, 345), (120, 300), (160, 390), (220, 340))
    doc.saveIncr()
    doc.close()

    result = SignatureAnalyzer().analyze(path)
    assert {p.party_name: p.signature_detected for p in result.parties} == {"Acme Retail Inc.": False, "Zenith Cloud LLC": True}


def test_chunks_respect_limit_and_abbreviations():
    """No chunk passes the limit, and "Pvt. Ltd." does not end a sentence."""
    long_sentence = "Provider shall deliver " + "the services " * 300 + "on time."
    pieces = split_large_text(long_sentence, 1800)
    assert len(pieces) > 1
    assert all(len(p) <= 1800 for p in pieces)
    assert " ".join(pieces).split() == long_sentence.split()

    filler = "Provider shall deliver the services on time. " * 45
    text = f"{filler}Payment goes to Lumenfield Pvt. Ltd. within thirty days. {filler}"
    joined = split_large_text(text, 1800)
    assert any("Lumenfield Pvt. Ltd. within thirty days." in p for p in joined)


def test_sentence_across_pages_stays_in_one_chunk():
    """A sentence running onto the next page is kept whole, so its quote can pass the check."""
    pages = [
        {"page_number": 1, "text": "4. TERMINATION\n4.1 Either Party may end this. 4.2 Provider may terminate this Agreement upon"},
        {"page_number": 2, "text": "fifteen days' written notice to Customer. 4.3 Customer may terminate later."},
    ]
    chunks = chunk_pages(pages)
    quote = "Provider may terminate this Agreement upon fifteen days' written notice to Customer."
    assert any(quote_in_text(quote, c.text) for c in chunks)
    assert all(c.section == "4. TERMINATION" for c in chunks)

    # A finished page is left alone
    finished = [{"page_number": 1, "text": "Done here."}, {"page_number": 2, "text": "new sentence."}]
    assert chunk_pages(finished)[0].text == "Done here."


def test_keyword_search_handles_word_forms_and_everyday_wording():
    """terminate/terminated/termination match, and everyday wording finds contract terms."""
    bm25 = BM25Index()
    bm25.index([
        {"chunk_id": "a", "text": "Either party may seek termination of this Agreement for convenience.", "metadata": {}},
        {"chunk_id": "b", "text": "Provider will host the application in a secure data centre.", "metadata": {}},
        {"chunk_id": "c", "text": "Customer shall not solicit employees of Provider.", "metadata": {}},
    ])
    assert bm25.search("terminated", top_k=1)[0]["chunk_id"] == "a"
    assert bm25.search(expand_query("Can they walk away?"), top_k=1)[0]["chunk_id"] == "a"


def _price_cap_status(text: str):
    results = MissingClauseDetector().detect(text)
    return next((r["status"] for r in results if r["check_id"] == "price-increase-cap"), None)


def test_price_cap_needs_a_real_price_sentence():
    """An unrelated percentage does not count as a cap on fees; a real cap does."""
    unrelated = "Customer shall pay fees of $100 per month. Uptime will increase to 99.5% next year."
    assert _price_cap_status(unrelated) == "MISSING"

    capped = "Customer shall pay fees of $100 per month. Fees shall not increase by more than 3% annually upon renewal."
    assert _price_cap_status(capped) == "PRESENT"


def test_price_cap_checked_without_a_pricing_table():
    """Fees written in a sentence are still checked; a contract with no fees skips the check."""
    assert _price_cap_status("The subscription fee is INR 50,000 per year, payable in advance.") == "MISSING"
    assert _price_cap_status("Each Party shall keep the other's Confidential Information secret.") is None


def test_rupee_sign_restored_only_from_symbol_font():
    """The sample PDF draws ₹ with a symbol font; those cells read ₹, not n."""
    tables = TableExtractor().extract_tables(PDF_PATH)
    pricing = next(t for t in tables if t.table_type == "pricing_tiers")
    assert "₹85,000" in str(pricing.rows)
    assert "n85,000" not in str(pricing.rows)
    # Ordinary text in other tables is untouched
    notices = next(t for t in tables if t.table_type == "notices_contacts")
    assert "Bengaluru" in str(notices.rows)


def test_footer_logo_is_not_a_signature(tmp_path):
    """An image at the bottom of the signing page sits outside every block."""
    path = _signed_pdf(tmp_path / "footer.pdf")
    doc = pymupdf.open(path)
    pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 8, 8))
    pixmap.clear_with(120)
    doc[0].insert_image(pymupdf.Rect(60, 760, 140, 800), pixmap=pixmap)
    doc.saveIncr()
    doc.close()

    result = SignatureAnalyzer().analyze(path)
    assert result.overall_status == "UNEXECUTED_DRAFT"


def test_signing_page_found_with_any_wording_and_all_parties_read(tmp_path):
    """Lower-case headings and "Executed by" are found, and a third signer is not dropped."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 60), "Signatures")
    page.insert_text((72, 120), "Executed by Acme Retail Inc.")
    page.insert_text((72, 140), "Signature: /s/ Ann Lee")
    page.insert_text((72, 260), "For Zenith Cloud LLC")
    page.insert_text((72, 280), "Signature: __________")
    page.insert_text((72, 400), "SIGNED FOR Orbit Guarantee Ltd")
    page.insert_text((72, 420), "Signature: /s/ Raj Mehta")
    path = tmp_path / "three.pdf"
    doc.save(path)
    doc.close()

    result = SignatureAnalyzer().analyze(path)
    assert result.signature_page == 1
    assert {p.party_name: p.signature_detected for p in result.parties} == {
        "Acme Retail Inc.": True,
        "Zenith Cloud LLC": False,
        "Orbit Guarantee Ltd": True,
    }
    assert result.overall_status == "PARTIALLY_EXECUTED"
    assert result.parties[2].party_role == "Other Party"


def test_verifier_fallback_is_flagged_and_uses_a_different_model(monkeypatch):
    """A verdict from the OpenAI backup is labelled, and is not from the Auditor's model."""
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.delenv("OPENAI_VERIFIER_MODEL", raising=False)
    verifier = GeminiVerifier()
    assert verifier.openai_model != "gpt-4o-mini"

    monkeypatch.setattr(verifier, "_gemini_verify", lambda prompt: (None, ""))
    monkeypatch.setattr(verifier, "_openai_verify", lambda prompt: ('{"verdict": "ACCEPTED"}', "openai:gpt-4o"))
    assert verifier.verify(finding={"claim": "x"}, evidence=[])["verifier_is_fallback"] is True

    monkeypatch.setattr(verifier, "_gemini_verify", lambda prompt: ('{"verdict": "ACCEPTED"}', "gemini:test"))
    assert verifier.verify(finding={"claim": "x"}, evidence=[])["verifier_is_fallback"] is False


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
