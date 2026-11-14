import re
from pydantic import BaseModel, Field

from app.auditing.obligation_extractor import CUSTOMER_ROLES, PROVIDER_ROLES


# A defined role: ("Customer"), (the "Client"), (hereinafter known as "Seller"), (hereinafter referred to as the "Buyer")
DEFINED_ROLE = re.compile(
    r"\(\s*(?:hereinafter|herein|henceforth)?\s*(?:(?:referred to|known|called|defined)\s+)?(?:as\s+)?(?:the\s+)?"
    r"[\"\u201c\u201d']([A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)?)[\"\u201c\u201d']\s*\)"
)


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
            # The words the contract itself uses for each side, e.g. "Buyer" / "Seller"
            "customer_role": "Customer",
            "provider_role": "Provider",
        }

        # Each party is introduced as: <Name>, a <description> ... ("<Role>")
        # e.g. 'Northstar Analytics Pvt. Ltd., a company ... ("Customer")'
        #      'Acme Retail Inc., a Delaware corporation ("Client")'
        role_words = {
            "customer": CUSTOMER_ROLES,
            "provider": PROVIDER_ROLES,
        }
        for key, roles in role_words.items():
            role_pattern = "|".join(roles)
            match = re.search(
                # (?-i:[A-Z]): the name must start with a real capital, so "by and between X" yields X
                r"(?:between|and)\s+((?-i:[A-Z])[A-Za-z0-9&\s\.\-]{2,60}?)"
                r"(?:,\s*an?\s+[^()]*?)?\s*\(\s*[\"“”']?\s*(?:the\s+)?(?:" + role_pattern + r")\s*[\"“”']?\s*\)",
                re.sub(r"\s+", " ", combined_text),
                re.IGNORECASE,
            )
            if match:
                parties[key] = match.group(1).strip(" ,")

        # Role names the contract defines, e.g. (hereinafter known as "Seller") or ("Client")
        flat = re.sub(r"\s+", " ", combined_text)
        for role_match in DEFINED_ROLE.finditer(flat):
            role = role_match.group(1).strip()
            word = role.lower().split()[-1]
            key = "provider" if word in PROVIDER_ROLES else "customer" if word in CUSTOMER_ROLES else None
            if not key or parties[f"{key}_role"] != key.capitalize():
                continue
            parties[f"{key}_role"] = role
            # No real name (a blank template) -> call the side by its role, not "Customer"
            if parties[key] == key.capitalize():
                name = self._name_before(flat[: role_match.start()])
                parties[key] = name or role

        return parties

    @staticmethod
    def _name_before(text: str) -> str | None:
        """The party name just before its role definition, if one is filled in."""
        after = re.split(r"\b(?:between|among|and)\b", text[-160:])[-1]
        name = re.split(r",|\bof\b|\(", after)[0].strip(" ,")
        if not name or "_" in name or not re.match(r"[A-Z]", name) or len(name) > 60:
            return None
        return name

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

    # Probes for a sale of goods (a vehicle, equipment, stock), judged from the Buyer's side
    SALE_OF_GOODS_PROBE_TEMPLATES = [
        {
            "probe_id": "probe-goods-warranty",
            "category": "warranties",
            "target_area": "Warranties & 'As Is' Sale",
            "keywords": ["warrant", "as is", "as-is", "merchantab", "condition"],
            "query_template": (
                "Does the seller give any warranty about the condition of the goods, or are they sold 'as is' "
                "with warranties disclaimed? What can the buyer do if hidden defects appear after delivery?"
            ),
            "priority": "critical",
            "expected_type": "deal_breaker",
        },
        {
            "probe_id": "probe-goods-risk-of-loss",
            "category": "delivery",
            "target_area": "Delivery & Risk of Loss",
            "keywords": ["deliver", "risk of loss", "possession"],
            "query_template": (
                "When does risk of loss pass to the buyer, and what happens if the goods are damaged, or the buyer "
                "or seller misses the delivery date?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-goods-payment",
            "category": "payment",
            "target_area": "Payment, Deposit & Refunds",
            "keywords": ["purchase price", "payment", "down-payment", "down payment", "deposit"],
            "query_template": (
                "How and when must the buyer pay, is any money due before delivery, and is it refundable if the "
                "seller does not deliver?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-goods-title",
            "category": "title",
            "target_area": "Title & Liens",
            "keywords": ["title", "lien", "encumbr", "registration"],
            "query_template": (
                "When does title pass to the buyer, and does the seller promise the goods are free of liens, "
                "loans or other claims?"
            ),
            "priority": "high",
            "expected_type": "watch_out",
        },
        {
            "probe_id": "probe-goods-insurance",
            "category": "insurance",
            "target_area": "Insurance, Registration & Handover",
            "keywords": ["insurance", "registration", "plates", "tags"],
            "query_template": (
                "What happens to insurance, registration, plates or tags at handover, and is the buyer left "
                "uninsured at any point?"
            ),
            "priority": "medium",
            "expected_type": "watch_out",
        },
    ]

    PROBES_BY_TYPE = {
        "services": ["GENERIC_PROBE_TEMPLATES"],
        "sale_of_goods": ["SALE_OF_GOODS_PROBE_TEMPLATES", "probe-indemnification", "probe-confidentiality"],
        "general": ["GENERIC_PROBE_TEMPLATES"],
        "not_a_contract": [],
    }

    def templates_for(self, contract_type: str = "services") -> list[dict]:
        templates: list[dict] = []
        generic = {t["probe_id"]: t for t in self.GENERIC_PROBE_TEMPLATES}
        for entry in self.PROBES_BY_TYPE.get(contract_type, ["GENERIC_PROBE_TEMPLATES"]):
            templates.extend(getattr(self, entry) if entry.isupper() else [generic[entry]])
        return templates

    def _match_section_to_probe(self, section_name: str, templates: list[dict] | None = None) -> str | None:
        """Try to match a detected section to a probe template by keywords."""
        sec_lower = section_name.lower()
        for template in templates if templates is not None else self.GENERIC_PROBE_TEMPLATES:
            if any(kw in sec_lower for kw in template["keywords"]):
                return template["probe_id"]
        return None

    def _build_probe_query(
        self, template: dict, section_name: str | None = None, parties: dict | None = None
    ) -> str:
        """Build a probe query, optionally grounded to a specific section and named for the contract's roles."""
        base_query = template["query_template"]
        parties = parties or {}
        customer_role = parties.get("customer_role", "Customer")
        provider_role = parties.get("provider_role", "Provider")
        if (customer_role, provider_role) != ("Customer", "Provider"):
            # Tell the auditor which side is which when the contract uses other words
            base_query = (
                f"Reviewing for the {customer_role} (the Customer side; the {provider_role} is the Provider side). "
                f"{base_query}"
            )
        if section_name:
            return f"Under '{section_name}': {base_query}"
        return base_query

    def create_plan(
        self,
        chunks: list[dict],
        document_title: str = "Master Services Agreement",
        contract_type: str = "services",
    ) -> AuditPlan:
        """
        Creates an end-to-end audit plan for the provided document.
        Dynamically generates probes based on the actual document sections found,
        falling back to generic probes for standard commercial areas.
        """
        parties = self.extract_parties(chunks)
        detected_sections = self.detect_sections(chunks)
        templates = self.templates_for(contract_type)

        # Map detected sections to probe templates
        section_probe_map: dict[str, str | None] = {}
        matched_probe_ids: set[str] = set()
        for sec in detected_sections:
            probe_id = self._match_section_to_probe(sec, templates)
            if probe_id:
                section_probe_map[sec] = probe_id
                matched_probe_ids.add(probe_id)

        # Build a lookup of templates by probe_id
        template_by_id = {t["probe_id"]: t for t in templates}

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
                    query=self._build_probe_query(template, section_name=sec, parties=parties),
                    priority=template["priority"],
                    expected_type=template["expected_type"],
                    target_sections=[sec],
                ))
                used_probe_ids.add(probe_id)

        # Second: add generic probes for areas not covered by detected sections
        for template in templates:
            if template["probe_id"] not in used_probe_ids:
                # Check if any chunk text mentions this topic at all
                combined_text = " ".join(c.get("text", "") for c in chunks).lower()
                if any(kw in combined_text for kw in template["keywords"]):
                    probes.append(AuditProbe(
                        probe_id=template["probe_id"],
                        category=template["category"],
                        target_area=template["target_area"],
                        query=self._build_probe_query(template, parties=parties),
                        priority=template["priority"],
                        expected_type=template["expected_type"],
                        target_sections=[],
                    ))
                    used_probe_ids.add(template["probe_id"])

        # Fallback safeguard: if no probes matched, include core generic probes so any document is audited
        if not probes and contract_type != "not_a_contract":
            for template in templates[:5]:
                probes.append(AuditProbe(
                    probe_id=template["probe_id"],
                    category=template["category"],
                    target_area=template["target_area"],
                    query=self._build_probe_query(template, parties=parties),
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

