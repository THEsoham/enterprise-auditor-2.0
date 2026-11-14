"""Contract type, unfilled templates, party roles and lettered sections (vehicle-sale style contracts)."""

from pathlib import Path

import pymupdf

from app.auditing.audit_planner import AuditPlanner
from app.auditing.contract_profile import profile_contract
from app.auditing.missing_clauses import MissingClauseDetector
from app.auditing.obligation_extractor import ObligationExtractor
from app.chunking.semantic_chunker import chunk_pages
from app.ingestion.table_extractor import TableExtractor
from app.scoring.health_score import HealthScore

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A blank vehicle-sale template in the style of common online forms
VEHICLE_TEMPLATE = """VEHICLE SALES AGREEMENT
THIS VEHICLE SALES AGREEMENT is made this ____ day of ____________, 20___, by and
among _______________________ of _________________________ (hereinafter known as
"Seller") and ______________, of ____________________ (hereinafter known as "Buyer").
Buyer and Seller shall collectively be known herein as "the Parties".
WHEREAS, Seller desires to sell the vehicle described below;
IN CONSIDERATION of the mutual promises, the Parties hereby agree as follows:
A. Description of Acquired Vehicle.
1. Make: __________
2. Model: __________
7. Vehicle Identification Number ("VIN"): __________________________
B. Consideration.
1. Purchase Price. The total purchase price to be paid by Buyer to Seller is ____ dollars ($_______).
i. Down-payment: $__________ (Due to Seller on or before execution of this agreement.)
C. Delivery of Acquired Vehicle and Conveyance of Title
1. Delivery of Acquired Vehicle. Seller shall deliver the Acquired Vehicle on or before __________ ("Delivery Date").
If Buyer fails to appear on or before the Delivery Date, then risk of loss passes to the Buyer on the Delivery Date.
2. Conveyance of Title. Seller shall convey title to Buyer upon delivery of the vehicle to Buyer.
D. Representations, Warranties, and Disclosures
1. Warranties. This vehicle is sold "AS IS", and Seller does not in any way, expressly or impliedly, give any warranties to Buyer.
E. Buyer's Responsibility. Buyer acknowledges that any insurance maintained by Seller on the Acquired Vehicle shall be canceled upon delivery.
M. State Law. This Agreement shall be interpreted under, and governed by, the laws of the state of ___________________.
IN WITNESS WHEREOF, Seller and Buyer affix their signatures hereto.
SELLER                     BUYER
Name: ______________       Name: ______________
Dated: _____________       Dated: _____________
"""

JOB_DESCRIPTION = """HashedIn Trainee Engineer - interview preparation guide
Round 1: online test with two coding questions. Round 2: technical interview.
Practise arrays, strings, SQL joins and OOP. Normalisation removes redundancy.
"""


def _pages(text: str) -> list[dict]:
    return [{"page_number": 1, "text": text}]


def _pdf_text(path: Path) -> str:
    with pymupdf.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def test_vehicle_sale_is_a_sale_of_goods_template():
    profile = profile_contract(VEHICLE_TEMPLATE)
    assert profile.is_contract and profile.contract_type == "sale_of_goods"
    assert profile.is_template
    assert "price / payment amount" in profile.blank_examples


def test_signature_blanks_alone_do_not_make_a_template():
    profile = profile_contract(_pdf_text(PROJECT_ROOT / "data" / "documents" / "sample_contract.pdf"))
    assert profile.contract_type == "services"
    assert not profile.is_template


def test_a_job_description_is_not_a_contract():
    profile = profile_contract(JOB_DESCRIPTION)
    assert not profile.is_contract and profile.contract_type == "not_a_contract"
    assert AuditPlanner().create_plan([{"text": JOB_DESCRIPTION}], contract_type="not_a_contract").probes == []
    assert MissingClauseDetector().detect(JOB_DESCRIPTION, contract_type="not_a_contract") == []


def test_sale_of_goods_checklist_flags_as_is_and_unprotected_deposit():
    results = {r["check_id"]: r for r in MissingClauseDetector().detect(VEHICLE_TEMPLATE, "sale_of_goods")}

    assert results["goods-condition-warranty"]["status"] == "MISSING"
    assert results["goods-condition-warranty"]["risk_level"] == "critical"
    assert "AS IS" in results["goods-condition-warranty"]["evidence_snippet"]
    assert results["clear-title-warranty"]["status"] == "MISSING"
    assert results["deposit-refund"]["status"] == "MISSING"
    assert results["risk-of-loss"]["status"] == "PRESENT"
    assert results["governing-law"]["status"] == "VAGUE"  # named, but the state is blank
    # Software-contract checks do not apply to a car sale
    assert "disaster-recovery-sla" not in results and "cyber-insurance-requirements" not in results


def test_party_roles_come_from_the_contract():
    parties = AuditPlanner().extract_parties(VEHICLE_TEMPLATE)
    assert parties["provider_role"] == "Seller" and parties["customer_role"] == "Buyer"
    # The names are blank in the template, so each side is called by its role
    assert parties["provider"] == "Seller" and parties["customer"] == "Buyer"


def test_named_parties_keep_their_names():
    text = 'This Agreement is made by and between Acme Motors Ltd., a company ("Seller") and Ravi Kumar ("Buyer").'
    parties = AuditPlanner().extract_parties(text)
    assert parties["provider"] == "Acme Motors Ltd." and parties["provider_role"] == "Seller"


def test_sale_of_goods_probes_are_asked_from_the_buyers_side():
    plan = AuditPlanner().create_plan([{"text": VEHICLE_TEMPLATE}], contract_type="sale_of_goods")
    ids = [p.probe_id for p in plan.probes]
    assert ids[0] == "probe-goods-warranty"
    assert "probe-data-retention" not in ids
    assert plan.probes[0].query.startswith("Reviewing for the Buyer")


def test_lettered_headings_become_sections():
    sections = {c.section for c in chunk_pages(_pages(VEHICLE_TEMPLATE))}
    assert "A. Description of Acquired Vehicle" in sections
    assert "C. Delivery of Acquired Vehicle and Conveyance of Title" in sections
    assert "D. Representations, Warranties, and Disclosures" in sections


def test_a_lettered_sentence_is_not_a_heading():
    text = "1. SERVICES\nA. The Seller shall deliver the goods on time.\nB. Payment. Buyer pays on delivery."
    sections = {c.section for c in chunk_pages(_pages(text))}
    assert "B. Payment" in sections
    assert not any(s and s.startswith("A. The Seller") for s in sections)


def test_definitions_are_not_obligations_and_acknowledgements_belong_to_the_speaker():
    chunks = [c.model_dump() for c in chunk_pages(_pages(VEHICLE_TEMPLATE))]
    result = ObligationExtractor().extract(chunks, parties={"customer": "Buyer", "provider": "Seller"})
    every = result.provider_obligations + result.customer_obligations + result.mutual_obligations

    assert not any("collectively be known" in o.duty for o in every)
    insurance = next(o for o in every if "insurance" in o.duty)
    assert insurance.party == "Customer"  # "Buyer acknowledges ..."
    assert any(o.party == "Provider" and "convey title" in o.duty for o in every)


def test_unfilled_template_score_is_capped():
    profile = profile_contract(VEHICLE_TEMPLATE).model_dump()
    result = HealthScore().calculate(findings=[], risk_scores=[], missing_clauses=[], profile=profile)
    assert result["health_score"] == HealthScore.TEMPLATE_SCORE_CAP
    assert result["rating"] == "Incomplete Draft"
    assert "Unfilled template" in result["warnings"][0]


def test_a_document_that_is_not_a_contract_is_not_scored():
    profile = profile_contract(JOB_DESCRIPTION).model_dump()
    result = HealthScore().calculate(findings=[], risk_scores=[], missing_clauses=[], profile=profile)
    assert result["health_score"] is None and result["rating"] == "Not a Contract"


def test_missing_critical_protection_costs_more_than_a_low_one():
    engine = HealthScore()
    critical = engine.calculate([], [], [{"status": "MISSING", "risk_level": "critical"}])["health_score"]
    low = engine.calculate([], [], [{"status": "MISSING", "risk_level": "low"}])["health_score"]
    assert critical < low


def test_boxed_text_is_not_a_table(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    # A code sample in a box: ruled lines, but one column of prose
    page.draw_rect(pymupdf.Rect(50, 100, 500, 300), width=1)
    page.draw_rect(pymupdf.Rect(50, 100, 500, 140), width=1)
    page.insert_textbox(pymupdf.Rect(55, 105, 495, 295), "SELECT name FROM employee WHERE salary > 100; " * 12, fontsize=9)
    # A real two-column table with a wrapped header
    for r, row in enumerate([["Took the\ntest", "Selected"], ["120", "8"]]):
        for c, value in enumerate(row):
            rect = pymupdf.Rect(50 + c * 150, 400 + r * 45, 200 + c * 150, 445 + r * 45)
            page.draw_rect(rect, width=0.7)
            page.insert_textbox(rect + (4, 2, -4, -2), value, fontsize=9)
    path = tmp_path / "boxes.pdf"
    doc.save(path)

    tables = TableExtractor().extract_tables(path)
    assert len(tables) == 1
    assert tables[0].headers == ["Took the test", "Selected"]
