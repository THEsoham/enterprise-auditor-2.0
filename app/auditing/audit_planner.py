import re
from typing import Optional
from pydantic import BaseModel, Field


class AuditProbe(BaseModel):
    probe_id: str
    category: str
    target_area: str
    query: str
    priority: str = "high"  # critical, high, medium
    expected_type: str = "risk_or_protection"
    target_sections: list[str] = Field(default_factory=list)


class AuditPlan(BaseModel):
    document_title: str = "Master Services Agreement"
    parties: dict[str, str] = Field(default_factory=dict)
    detected_sections: list[str] = Field(default_factory=list)
    probes: list[AuditProbe] = Field(default_factory=list)


class AuditPlanner:
    """
    Autonomous Document Analyzer and Audit Planner.
    Inspects document structure, extracts parties, identifies sections,
    and dynamically compiles targeted audit probes across all core commercial domains:
    - Termination & Parity
    - Liability Caps & Exceptions
    - Data Security & Retention
    - Subcontractor Accountability
    - Term & Auto-Renewal
    - Audit Rights & Oversight
    - Publicity & Logo Use
    - IP Ownership & Data Rights
    - Confidentiality
    - Indemnification & Defense
    - Payment Terms & Late Penalties
    - Non-Solicitation
    - Cross-Clause Asymmetry
    """

    CORE_AUDIT_PROBES = [
        {
            "probe_id": "probe-termination-asymmetry",
            "category": "termination",
            "target_area": "Termination & Asymmetry",
            "query": (
                "What are the Provider's and Customer's convenience termination rights and notice periods "
                "under Section 10? Are the rights and notice periods asymmetric between the parties?"
            ),
            "priority": "critical",
            "expected_type": "deal_breaker",
            "target_sections": ["10. TERMINATION"],
        },
        {
            "probe_id": "probe-liability-cap",
            "category": "liability",
            "target_area": "Limitation of Liability",
            "query": (
                "What is the aggregate liability cap under Section 9? How many months of fees does it cover, "
                "and does it leave the Customer under-protected?"
            ),
            "priority": "critical",
            "expected_type": "deal_breaker",
            "target_sections": ["9. LIMITATION OF LIABILITY"],
        },
        {
            "probe_id": "probe-data-backup-retention",
            "category": "data_security",
            "target_area": "Backup Data Retention",
            "query": (
                "What happens to backup copies of Customer Data after deletion under Section 4? "
                "How many days may the Provider retain backup data in its systems?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
            "target_sections": ["4. DATA PROCESSING AND SECURITY"],
        },
        {
            "probe_id": "probe-subcontractor-liability",
            "category": "data_security",
            "target_area": "Subcontractor Accountability",
            "query": (
                "Does the Provider remain responsible for the acts and omissions of its subcontractors "
                "under Section 4? Is this a Customer protection?"
            ),
            "priority": "high",
            "expected_type": "protection",
            "target_sections": ["4. DATA PROCESSING AND SECURITY"],
        },
        {
            "probe_id": "probe-term-auto-renewal",
            "category": "term_renewal",
            "target_area": "Term & Automatic Renewal",
            "query": (
                "Does the contract automatically renew under Section 14? What is the non-renewal notice period "
                "required to prevent automatic renewal?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
            "target_sections": ["14. TERM AND RENEWAL"],
        },
        {
            "probe_id": "probe-customer-audit-rights",
            "category": "audit_compliance",
            "target_area": "Audit Rights & Verification",
            "query": (
                "What are the Customer's security audit rights under Section 18? How much advance notice is required "
                "and can the Provider substitute third-party reports?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
            "target_sections": ["18. AUDIT RIGHTS"],
        },
        {
            "probe_id": "probe-publicity-logo",
            "category": "publicity",
            "target_area": "Publicity & Brand Rights",
            "query": (
                "Can the Provider use the Customer's name or logo in presentations and marketing materials "
                "without Customer's prior consent under Section 19?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
            "target_sections": ["19. PUBLICITY"],
        },
        {
            "probe_id": "probe-ip-ownership",
            "category": "intellectual_property",
            "target_area": "Customer Data Ownership",
            "query": (
                "Does Customer retain all right, title, and interest in Customer Data under Section 6? "
                "What license is granted to the Provider?"
            ),
            "priority": "high",
            "expected_type": "protection",
            "target_sections": ["6. INTELLECTUAL PROPERTY"],
        },
        {
            "probe_id": "probe-confidentiality-mutuality",
            "category": "confidentiality",
            "target_area": "Confidentiality Obligations",
            "query": (
                "Are confidentiality obligations bilateral and mutual under Section 5? "
                "What standard of care is required to protect confidential information?"
            ),
            "priority": "high",
            "expected_type": "protection",
            "target_sections": ["5. CONFIDENTIALITY"],
        },
        {
            "probe_id": "probe-indemnification-parity",
            "category": "indemnification",
            "target_area": "Indemnification Parity & Defense",
            "query": (
                "What are the indemnification obligations of each party under Section 8? "
                "Does Provider defend Customer against third-party IP infringement claims?"
            ),
            "priority": "high",
            "expected_type": "protection",
            "target_sections": ["8. INDEMNIFICATION"],
        },
        {
            "probe_id": "probe-fees-suspension",
            "category": "payment",
            "target_area": "Payment Terms & Suspension",
            "query": (
                "What is the invoice payment period under Section 3, what interest accrues on late payments, "
                "and under what conditions can Provider suspend services?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
            "target_sections": ["3. FEES AND PAYMENT"],
        },
        {
            "probe_id": "probe-non-solicitation",
            "category": "restrictive_covenants",
            "target_area": "Non-Solicitation Period",
            "query": (
                "What is the non-solicitation restriction under Section 11, and how long does it last "
                "after the contract ends?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
            "target_sections": ["11. NON-SOLICITATION"],
        },
    ]

    def extract_parties(self, text_or_chunks: str | list[dict]) -> dict[str, str]:
        """Extract customer and provider party names from preamble text."""
        combined_text = ""
        if isinstance(text_or_chunks, list):
            for c in text_or_chunks[:4]:
                if isinstance(c, dict):
                    combined_text += " " + c.get("text", "")
                elif hasattr(c, "text"):
                    combined_text += " " + getattr(c, "text", "")
        else:
            combined_text = str(text_or_chunks)

        parties = {
            "customer": "Customer",
            "provider": "Provider",
        }

        # Match: "Northstar Analytics Pvt. Ltd. ... Customer"
        cust_match = re.search(
            r"between\s+([A-Z][A-Za-z0-9\s\.\-]{2,50}?)(?:,\s*a\s+company[^\(\)]*?)?\s*\([^\)]*?Customer[^\)]*?\)",
            combined_text,
            re.IGNORECASE
        )
        if cust_match:
            parties["customer"] = cust_match.group(1).strip(" ,")

        # Match: "Meridian Cloud Systems Pvt. Ltd. ... Provider"
        prov_match = re.search(
            r"and\s+([A-Z][A-Za-z0-9\s\.\-]{2,50}?)(?:,\s*a\s+company[^\(\)]*?)?\s*\([^\)]*?Provider[^\)]*?\)",
            combined_text,
            re.IGNORECASE
        )
        if prov_match:
            parties["provider"] = prov_match.group(1).strip(" ,")

        return parties

    def detect_sections(self, chunks: list[dict]) -> list[str]:
        """Extract detected section titles from chunk metadata or text."""
        sections = set()
        for c in chunks:
            if isinstance(c, dict):
                sec = c.get("section") or c.get("metadata", {}).get("section")
            else:
                sec = getattr(c, "section", None)

            if sec:
                sections.add(sec.strip())

        return sorted(list(sections))

    def create_plan(
        self,
        chunks: list[dict],
        document_title: str = "Master Services Agreement"
    ) -> AuditPlan:
        """
        Creates an end-to-end audit plan for the provided document.
        Combines detected sections and party names to formulate grounded probes.
        """
        parties = self.extract_parties(chunks)
        detected_sections = self.detect_sections(chunks)

        probes = []
        for p in self.CORE_AUDIT_PROBES:
            probes.append(AuditProbe(
                probe_id=p["probe_id"],
                category=p["category"],
                target_area=p["target_area"],
                query=p["query"],
                priority=p["priority"],
                expected_type=p["expected_type"],
                target_sections=p["target_sections"],
            ))

        return AuditPlan(
            document_title=document_title,
            parties=parties,
            detected_sections=detected_sections,
            probes=probes,
        )
