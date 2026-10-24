import re
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

    # Generic probe templates that adapt to any document structure
    GENERIC_PROBE_TEMPLATES = [
        {
            "probe_id": "probe-termination",
            "category": "termination",
            "target_area": "Termination & Asymmetry",
            "keywords": ["terminat", "cancel", "exit", "convenience"],
            "query_template": (
                "What are the termination rights and notice periods for each party? "
                "Are the rights and notice periods asymmetric between the parties?"
            ),
            "priority": "critical",
            "expected_type": "deal_breaker",
        },
        {
            "probe_id": "probe-liability",
            "category": "liability",
            "target_area": "Limitation of Liability",
            "keywords": ["liabilit", "damages", "cap", "aggregate"],
            "query_template": (
                "What is the aggregate liability cap? How many months of fees does it cover, "
                "and does it leave one party under-protected?"
            ),
            "priority": "critical",
            "expected_type": "deal_breaker",
        },
        {
            "probe_id": "probe-data-retention",
            "category": "data_security",
            "target_area": "Data Retention & Backup",
            "keywords": ["data", "backup", "retention", "deletion", "destroy"],
            "query_template": (
                "What happens to data after deletion or contract termination? "
                "How long may data be retained in backups?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-subcontractor",
            "category": "data_security",
            "target_area": "Subcontractor Accountability",
            "keywords": ["subcontract", "third party", "third-party", "sub-process"],
            "query_template": (
                "Is a party responsible for the acts and omissions of its subcontractors? "
                "Is this a protection for the other party?"
            ),
            "priority": "high",
            "expected_type": "protection",
        },
        {
            "probe_id": "probe-renewal",
            "category": "term_renewal",
            "target_area": "Term & Automatic Renewal",
            "keywords": ["renew", "auto-renew", "term", "expir"],
            "query_template": (
                "Does the contract automatically renew? What is the non-renewal notice period "
                "required to prevent automatic renewal?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-audit-rights",
            "category": "audit_compliance",
            "target_area": "Audit Rights & Verification",
            "keywords": ["audit", "inspect", "verification", "compliance"],
            "query_template": (
                "What are the audit or inspection rights? How much advance notice is required "
                "and can a party substitute third-party reports?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-publicity",
            "category": "publicity",
            "target_area": "Publicity & Brand Rights",
            "keywords": ["publicit", "logo", "marketing", "brand", "reference"],
            "query_template": (
                "Can either party use the other's name or logo in marketing materials "
                "without prior consent?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-ip-ownership",
            "category": "intellectual_property",
            "target_area": "IP & Data Ownership",
            "keywords": ["intellectual property", "ownership", "license", "ip right"],
            "query_template": (
                "Who retains ownership of data and intellectual property? "
                "What licenses are granted?"
            ),
            "priority": "high",
            "expected_type": "protection",
        },
        {
            "probe_id": "probe-confidentiality",
            "category": "confidentiality",
            "target_area": "Confidentiality Obligations",
            "keywords": ["confidential", "non-disclosure", "proprietary", "trade secret"],
            "query_template": (
                "Are confidentiality obligations bilateral and mutual? "
                "What standard of care is required to protect confidential information?"
            ),
            "priority": "high",
            "expected_type": "protection",
        },
        {
            "probe_id": "probe-indemnification",
            "category": "indemnification",
            "target_area": "Indemnification & Defense",
            "keywords": ["indemnif", "defend", "hold harmless"],
            "query_template": (
                "What are the indemnification obligations of each party? "
                "Does either party defend the other against third-party claims?"
            ),
            "priority": "high",
            "expected_type": "protection",
        },
        {
            "probe_id": "probe-payment",
            "category": "payment",
            "target_area": "Payment Terms & Penalties",
            "keywords": ["payment", "invoice", "fee", "interest", "suspend"],
            "query_template": (
                "What is the invoice payment period, what interest accrues on late payments, "
                "and under what conditions can services be suspended?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-non-solicitation",
            "category": "restrictive_covenants",
            "target_area": "Non-Solicitation / Restrictive Covenants",
            "keywords": ["non-solicitation", "non-compete", "restrictive", "covenant"],
            "query_template": (
                "Are there non-solicitation or restrictive covenant provisions, and how long "
                "do they last after the contract ends?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
        },
    ]

    def _match_section_to_probe(self, section_name: str) -> str | None:
        """Try to match a detected section to a probe template by keywords."""
        sec_lower = section_name.lower()
        for template in self.GENERIC_PROBE_TEMPLATES:
            if any(kw in sec_lower for kw in template["keywords"]):
                return template["probe_id"]
        return None

    def _build_probe_query(self, template: dict, section_name: str | None = None) -> str:
        """Build a probe query, optionally grounded to a specific section."""
        base_query = template["query_template"]
        if section_name:
            return f"Under '{section_name}': {base_query}"
        return base_query

    def create_plan(
        self,
        chunks: list[dict],
        document_title: str = "Master Services Agreement"
    ) -> AuditPlan:
        """
        Creates an end-to-end audit plan for the provided document.
        Dynamically generates probes based on the actual document sections found,
        falling back to generic probes for standard commercial areas.
        """
        parties = self.extract_parties(chunks)
        detected_sections = self.detect_sections(chunks)

        # Map detected sections to probe templates
        section_probe_map: dict[str, str | None] = {}
        matched_probe_ids: set[str] = set()
        for sec in detected_sections:
            probe_id = self._match_section_to_probe(sec)
            if probe_id:
                section_probe_map[sec] = probe_id
                matched_probe_ids.add(probe_id)

        # Build a lookup of templates by probe_id
        template_by_id = {t["probe_id"]: t for t in self.GENERIC_PROBE_TEMPLATES}

        probes = []
        used_probe_ids: set[str] = set()

        # First: create section-grounded probes for detected sections
        for sec, probe_id in section_probe_map.items():
            if probe_id and probe_id not in used_probe_ids:
                template = template_by_id[probe_id]
                probes.append(AuditProbe(
                    probe_id=template["probe_id"],
                    category=template["category"],
                    target_area=template["target_area"],
                    query=self._build_probe_query(template, section_name=sec),
                    priority=template["priority"],
                    expected_type=template["expected_type"],
                    target_sections=[sec],
                ))
                used_probe_ids.add(probe_id)

        # Second: add generic probes for areas not covered by detected sections
        for template in self.GENERIC_PROBE_TEMPLATES:
            if template["probe_id"] not in used_probe_ids:
                # Check if any chunk text mentions this topic at all
                combined_text = " ".join(c.get("text", "") for c in chunks).lower()
                if any(kw in combined_text for kw in template["keywords"]):
                    probes.append(AuditProbe(
                        probe_id=template["probe_id"],
                        category=template["category"],
                        target_area=template["target_area"],
                        query=self._build_probe_query(template),
                        priority=template["priority"],
                        expected_type=template["expected_type"],
                        target_sections=[],
                    ))
                    used_probe_ids.add(template["probe_id"])

        # Fallback safeguard: if no probes matched, include core generic probes so any document is audited
        if not probes:
            for template in self.GENERIC_PROBE_TEMPLATES[:5]:
                probes.append(AuditProbe(
                    probe_id=template["probe_id"],
                    category=template["category"],
                    target_area=template["target_area"],
                    query=self._build_probe_query(template),
                    priority=template["priority"],
                    expected_type=template["expected_type"],
                    target_sections=[],
                ))

        # Sort by priority: critical > high > medium
        priority_order = {"critical": 0, "high": 1, "medium": 2}
        probes.sort(key=lambda p: priority_order.get(p.priority, 99))

        return AuditPlan(
            document_title=document_title,
            parties=parties,
            detected_sections=detected_sections,
            probes=probes,
        )

