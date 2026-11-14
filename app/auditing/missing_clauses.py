import re
from typing import Literal, Optional
from pydantic import BaseModel

from app.auditing.obligation_extractor import classify_party, split_sentences


MissingStatus = Literal["PRESENT", "MISSING", "VAGUE"]


class MissingClauseCheck(BaseModel):
    check_id: str
    title: str
    category: str
    status: MissingStatus
    risk_level: str  # critical, high, medium, low, none
    why_it_matters: str
    recommended_clause: str
    evidence_snippet: str = ""


class MissingClauseDetector:
    """
    Evaluates contracts against an Enterprise Protection Baseline
    to identify missing safeguards, vague commitments, and standard protections.
    Every PRESENT / VAGUE result quotes the sentence it was based on.
    """

    BASELINE_CHECKS = [
        {
            "id": "disaster-recovery-sla",
            "title": "Disaster Recovery SLA & RTO/RPO",
            "category": "business_continuity",
            "risk_level": "high",
            "why_it_matters": (
                "Without explicit Recovery Time / Recovery Point Objectives there is no contractual commitment "
                "for when service or data will be restored after a catastrophic outage."
            ),
            "recommended_clause": (
                "Provider shall maintain a business continuity and disaster recovery plan with a Recovery Time Objective (RTO) "
                "of not more than 4 hours and a Recovery Point Objective (RPO) of not more than 1 hour."
            ),
        },
        {
            "id": "security-incident-timeframe",
            "title": "Maximum Security Incident Notification Window",
            "category": "data_security",
            "risk_level": "critical",
            "why_it_matters": (
                "Breach notification should have an hour-based maximum (e.g. 24-72 hours). Wording such as "
                "'without undue delay' may cause the customer to miss regulatory reporting deadlines."
            ),
            "recommended_clause": (
                "Provider shall notify Customer in writing without undue delay, and in any event within forty-eight (48) hours, "
                "after becoming aware of or confirming any Security Incident involving Customer Data."
            ),
        },
        {
            "id": "data-return-destruction-certification",
            "title": "Affirmative Data Deletion & Certification",
            "category": "data_security",
            "risk_level": "high",
            "why_it_matters": (
                "The provider should be obliged to return or destroy all customer data at the end of the contract "
                "and certify the destruction in writing."
            ),
            "recommended_clause": (
                "Within thirty (30) days of termination, Provider shall, at Customer's election, return or permanently and securely "
                "destroy all Customer Data, and deliver written certification of compliance signed by an officer of Provider."
            ),
        },
        {
            "id": "subcontractor-advance-notice",
            "title": "Advance Notice of New Subprocessors",
            "category": "data_security",
            "risk_level": "medium",
            "why_it_matters": (
                "Subcontractors processing customer data should require advance notice and a right to object, "
                "otherwise compliance or data-residency policies may be breached without the customer knowing."
            ),
            "recommended_clause": (
                "Provider shall provide Customer with at least thirty (30) days' prior written notice before engaging any new subcontractor "
                "to process Customer Data, and Customer may object on reasonable security or compliance grounds."
            ),
        },
        {
            "id": "force-majeure-termination",
            "title": "Termination Right for Extended Force Majeure",
            "category": "termination",
            "risk_level": "medium",
            "why_it_matters": (
                "If a force majeure event lasts a long time, the customer should be able to exit the contract "
                "instead of paying for services that cannot be delivered."
            ),
            "recommended_clause": (
                "If a Force Majeure event prevents performance of the Services for more than thirty (30) consecutive days, "
                "Customer may terminate this Agreement immediately upon written notice without penalty."
            ),
        },
        {
            "id": "customer-convenience-termination-parity",
            "title": "Customer Convenience Termination Parity",
            "category": "termination",
            "risk_level": "high",
            "why_it_matters": (
                "When only one side can walk away for convenience, or on much shorter notice, "
                "the other side carries the risk of a sudden exit."
            ),
            "recommended_clause": (
                "Either Party may terminate this Agreement for convenience at any time upon sixty (60) days' prior written notice."
            ),
        },
        {
            "id": "cyber-insurance-requirements",
            "title": "Cyber Liability & E&O Insurance Commitments",
            "category": "risk_management",
            "risk_level": "medium",
            "why_it_matters": (
                "Technology Errors & Omissions and Cyber Liability insurance backstop the provider's "
                "indemnification and security commitments."
            ),
            "recommended_clause": (
                "Provider shall maintain commercial general liability insurance, technology errors & omissions, and cyber liability insurance "
                "with policy limits of not less than $5,000,000 per occurrence during the Term."
            ),
        },
        {
            "id": "confidentiality-clause-present",
            "title": "Confidentiality Clause",
            "category": "confidentiality",
            "risk_level": "high",
            "why_it_matters": "A confidentiality clause is a standard core protection for both parties.",
            "recommended_clause": (
                "Each Party shall protect the other Party's Confidential Information using at least reasonable care "
                "and use it only to perform this Agreement."
            ),
        },
        {
            "id": "liability-clause-present",
            "title": "Limitation of Liability Clause",
            "category": "liability",
            "risk_level": "high",
            "why_it_matters": "A limitation of liability clause defines the maximum financial exposure of each party.",
            "recommended_clause": (
                "Each Party's aggregate liability shall not exceed the fees paid or payable during the twelve (12) months "
                "preceding the event giving rise to the claim."
            ),
        },
        {
            "id": "termination-clause-present",
            "title": "Termination Clause",
            "category": "termination",
            "risk_level": "high",
            "why_it_matters": "A termination clause defines how and when either party can end the agreement.",
            "recommended_clause": (
                "Either Party may terminate this Agreement for material breach that remains uncured 30 days after written notice."
            ),
        },
        {
            "id": "price-increase-cap",
            "title": "Cap on Price Increases",
            "category": "commercial",
            "risk_level": "medium",
            "why_it_matters": (
                "Without a limit on fee increases (a maximum percentage or a CPI link), the provider can raise "
                "prices by any amount at renewal, whether the fees are listed in a table or in a sentence."
            ),
            "recommended_clause": (
                "Fees shall not increase by more than 3% (or the change in the Consumer Price Index, if lower) "
                "in any 12-month period, with at least 60 days' written notice of any increase."
            ),
        },
    ]

    # Protections a buyer of goods (a car, equipment, stock) should look for
    SALE_OF_GOODS_CHECKS = [
        {
            "id": "goods-condition-warranty",
            "title": "Warranty on Condition of the Goods",
            "category": "warranties",
            "risk_level": "critical",
            "why_it_matters": (
                "If the goods are sold 'as is' with all warranties disclaimed, the Buyer has no claim when "
                "hidden defects appear after delivery, even ones the Seller knew about."
            ),
            "recommended_clause": (
                "Seller warrants that the goods are free from material defects known to Seller, that all known "
                "defects have been disclosed in writing, and that the goods will be in the same condition at "
                "delivery as when inspected by Buyer."
            ),
        },
        {
            "id": "clear-title-warranty",
            "title": "Clear Title, Free of Liens",
            "category": "title",
            "risk_level": "high",
            "why_it_matters": (
                "A promise to transfer title is not a promise that the title is clean. Without a warranty that the "
                "goods are free of liens, loans or other claims, the Buyer can lose them to the Seller's lender."
            ),
            "recommended_clause": (
                "Seller warrants that it holds good and marketable title to the goods, free and clear of all liens, "
                "encumbrances and security interests, and will indemnify Buyer against any such claim."
            ),
        },
        {
            "id": "inspection-rejection-right",
            "title": "Buyer's Right to Inspect and Reject",
            "category": "acceptance",
            "risk_level": "medium",
            "why_it_matters": (
                "The Buyer should be able to inspect the goods before or at delivery and refuse them, with a refund, "
                "if they do not match the description."
            ),
            "recommended_clause": (
                "Buyer may inspect the goods at delivery and may reject them, with a full refund of all amounts paid, "
                "if they do not conform to the description in this Agreement."
            ),
        },
        {
            "id": "risk-of-loss",
            "title": "Risk of Loss Before Delivery",
            "category": "delivery",
            "risk_level": "medium",
            "why_it_matters": (
                "The contract should say who bears the loss if the goods are damaged, destroyed or stolen "
                "before the Buyer takes them."
            ),
            "recommended_clause": "Risk of loss remains with Seller until the goods are delivered to and accepted by Buyer.",
        },
        {
            "id": "deposit-refund",
            "title": "Refund of Deposit if the Seller Fails to Deliver",
            "category": "payment",
            "risk_level": "high",
            "why_it_matters": (
                "Money paid before delivery is at risk. The contract should promise it back if the Seller "
                "does not deliver on time or the sale falls through."
            ),
            "recommended_clause": (
                "If Seller fails to deliver the goods by the Delivery Date, Buyer may cancel this Agreement and Seller "
                "shall refund all amounts paid within seven (7) days."
            ),
        },
        {
            "id": "seller-default-remedy",
            "title": "Buyer's Remedy if the Seller Does Not Deliver",
            "category": "remedies",
            "risk_level": "medium",
            "why_it_matters": (
                "The contract should give the Buyer a clear right to cancel, get a refund or demand delivery if the "
                "Seller does not perform, instead of leaving the Buyer to sue for damages."
            ),
            "recommended_clause": (
                "If Seller fails to deliver the goods by the Delivery Date, Buyer may, at its option, cancel this "
                "Agreement with a full refund or require delivery within a further reasonable period."
            ),
        },
        {
            "id": "governing-law",
            "title": "Governing Law & Dispute Forum",
            "category": "disputes",
            "risk_level": "low",
            "why_it_matters": "The contract should name which law applies and where disputes are heard.",
            "recommended_clause": "This Agreement is governed by the laws of [State], and its courts have exclusive jurisdiction.",
        },
    ]

    # Which checks apply to which kind of contract (see contract_profile.py)
    CHECKS_BY_TYPE = {
        "services": None,  # every BASELINE_CHECKS item
        "sale_of_goods": "SALE_OF_GOODS_CHECKS",
        "general": ["termination-clause-present", "liability-clause-present", "confidentiality-clause-present", "governing-law"],
        "not_a_contract": [],
    }

    def checks_for(self, contract_type: str = "services") -> list[dict]:
        selection = self.CHECKS_BY_TYPE.get(contract_type)
        if selection is None:
            return self.BASELINE_CHECKS
        if isinstance(selection, str):
            return getattr(self, selection)
        every = {c["id"]: c for c in self.BASELINE_CHECKS + self.SALE_OF_GOODS_CHECKS}
        return [every[check_id] for check_id in selection]

    def detect(self, full_text: str, contract_type: str = "services") -> list[dict]:
        """Analyze full document text against the checks for its contract type."""
        sentences = split_sentences(full_text)
        text_lower = re.sub(r"\s+", " ", full_text).lower()
        results = []

        for check in self.checks_for(contract_type):
            handler = getattr(self, "_check_" + check["id"].replace("-", "_"))
            outcome = handler(sentences, text_lower)
            if outcome is None:
                # Not applicable to this contract (e.g. no fees at all)
                continue
            status, snippet = outcome

            results.append(MissingClauseCheck(
                check_id=check["id"],
                title=check["title"],
                category=check["category"],
                status=status,
                risk_level=check["risk_level"] if status != "PRESENT" else "none",
                why_it_matters=check["why_it_matters"],
                recommended_clause=check["recommended_clause"],
                evidence_snippet=snippet,
            ).model_dump())

        return results

    # --- helpers -------------------------------------------------------------

    @staticmethod
    def _find(sentences: list[str], pattern: str) -> Optional[str]:
        """First sentence matching the pattern (case-insensitive), as evidence."""
        regex = re.compile(pattern, re.IGNORECASE)
        return next((s for s in sentences if regex.search(s)), None)

    @staticmethod
    def _quote(sentence: Optional[str], limit: int = 240) -> str:
        if not sentence:
            return ""
        return sentence if len(sentence) <= limit else sentence[:limit].rsplit(" ", 1)[0] + "…"

    def _present_if(self, sentences: list[str], pattern: str, missing_note: str) -> tuple[MissingStatus, str]:
        sentence = self._find(sentences, pattern)
        if sentence:
            return "PRESENT", self._quote(sentence)
        return "MISSING", missing_note

    # --- checks --------------------------------------------------------------

    def _check_disaster_recovery_sla(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"\b(?:rto|rpo|recovery time objective|recovery point objective)\b",
            "No disaster recovery SLA or RTO/RPO targets found.",
        )

    def _check_security_incident_timeframe(self, sentences, text_lower):
        notice = self._find(sentences, r"security incident|data breach|personal data breach|unauthori[sz]ed access")
        strict = self._find(
            sentences,
            r"(?:within|no later than|in no event (?:more|later) than)\s+(?:[a-z\-]+\s+)?\(?\d{1,3}\)?\s*(?:hours|hrs)",
        )
        if strict:
            return "PRESENT", self._quote(strict)
        if notice:
            return "VAGUE", self._quote(notice)
        return "MISSING", "No security incident notification clause found."

    def _check_data_return_destruction_certification(self, sentences, text_lower):
        certified = self._find(
            sentences,
            r"written certification|certif\w*\b.{0,60}\b(?:destruction|deletion|destroyed|deleted)",
        )
        if certified:
            return "PRESENT", self._quote(certified)
        returned = self._find(sentences, r"\breturn\b.{0,40}\b(?:destroy|delete)|\b(?:destroy|delete)\b.{0,40}\breturn\b")
        if returned:
            return "VAGUE", self._quote(returned)
        return "MISSING", "No obligation to return or destroy customer data with written certification found."

    def _check_subcontractor_advance_notice(self, sentences, text_lower):
        mentions = [s for s in sentences if re.search(r"sub-?contractor|sub-?processor", s, re.IGNORECASE)]
        if not mentions:
            return "VAGUE", "The contract is silent on the use of subcontractors or subprocessors."
        with_notice = next(
            (s for s in mentions if re.search(r"prior (?:written )?notice|advance notice|right to object|may object", s, re.IGNORECASE)),
            None,
        )
        if with_notice:
            return "PRESENT", self._quote(with_notice)
        return "MISSING", self._quote(mentions[0])

    def _check_force_majeure_termination(self, sentences, text_lower):
        # Prefer the clause itself over passing mentions such as "excluding force majeure events"
        heading = re.search(r"\b\d{1,2}\.\s*force majeure\b", text_lower)
        start = heading.start() if heading else text_lower.find("beyond its reasonable control")
        if start < 0:
            start = text_lower.find("force majeure")
        if start < 0:
            return "MISSING", "No force majeure clause found."

        window = text_lower[start:start + 1200]
        clause = (
            self._find(sentences, r"beyond (?:its|their) reasonable control")
            or self._find(sentences, r"force majeure")
        )
        if re.search(r"terminat", window):
            return "PRESENT", self._quote(clause)
        return "MISSING", self._quote(clause)

    def _check_customer_convenience_termination_parity(self, sentences, text_lower):
        convenience = [
            s for s in sentences
            if re.search(r"terminat", s, re.IGNORECASE) and re.search(r"convenience|without cause", s, re.IGNORECASE)
        ]
        if not convenience:
            return "PRESENT", "Neither party has a convenience termination right."

        rights: dict[str, str] = {}
        for sentence in convenience:
            # "Client may not terminate for convenience" denies the right rather than granting it
            if re.search(r"\b(?:may not|shall not|cannot|can not|is not entitled to|has no right to)\b", sentence, re.IGNORECASE):
                continue
            verb = re.search(r"\b(?:may|can|shall have the right to)\b", sentence, re.IGNORECASE)
            party = classify_party(sentence[: verb.start()] if verb else sentence)
            if party and party not in rights:
                rights[party] = sentence

        if "Mutual" in rights:
            return "PRESENT", self._quote(rights["Mutual"])

        provider, customer = rights.get("Provider"), rights.get("Customer")
        if provider and not customer:
            return "MISSING", self._quote(provider)
        if provider and customer:
            restricted = re.search(r"only after|after the first|not before|no earlier than", customer, re.IGNORECASE)
            if restricted:
                return "MISSING", self._quote(f"{provider} / {customer}", 400)
            return "PRESENT", self._quote(f"{provider} / {customer}", 400)
        return "PRESENT", self._quote(customer or convenience[0])

    def _check_cyber_insurance_requirements(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"cyber (?:liability|insurance)|errors (?:and|&) omissions",
            "No insurance maintenance requirements found.",
        )

    def _check_confidentiality_clause_present(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"confidential information.{0,80}\b(?:shall|must|will)\b|\b(?:shall|must|will)\b.{0,80}confidential",
            "No confidentiality obligations found.",
        )

    def _check_liability_clause_present(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"limitation of liability|aggregate liability|liability.{0,80}shall not exceed|shall not be liable",
            "No limitation of liability clause found.",
        )

    def _check_termination_clause_present(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"\bterminat\w*\b.{0,40}\bagreement\b",
            "No termination clause found.",
        )

    def _check_price_increase_cap(self, sentences, text_lower):
        fee_pattern = r"\b(?:fees?|prices?|pricing|charges?|rates?|subscription)\b"
        money_pattern = r"(?:[$€£₹]|\b(?:inr|usd|rs\.?|eur|gbp)\b)\s?\d|\d[\d,]*(?:\.\d+)?\s?(?:per|/)\s?(?:month|year|annum|user|document)"
        charges_fees = any(
            re.search(fee_pattern, s, re.IGNORECASE) and re.search(money_pattern, s, re.IGNORECASE)
            for s in sentences
        )
        if not charges_fees:
            return None

        # A cap must be one sentence that links prices, an increase, and a limit,
        # so an unrelated percentage elsewhere in the contract does not count
        cap = next(
            (
                s for s in sentences
                if re.search(fee_pattern, s, re.IGNORECASE)
                and re.search(r"\b(?:increas|escalat|adjust|rais)\w*", s, re.IGNORECASE)
                and re.search(r"\d+(?:\.\d+)?\s*(?:%|percent)|\bcpi\b|consumer price index", s, re.IGNORECASE)
            ),
            None,
        )
        if cap:
            return "PRESENT", self._quote(cap)
        return "MISSING", "The contract charges fees but nothing limits how much they can rise."


    # --- sale of goods checks ------------------------------------------------

    def _check_goods_condition_warranty(self, sentences, text_lower):
        as_is = self._find(
            sentences,
            r"\bas[\s-]is\b|disclaims?\b.{0,60}\bwarrant|without (?:any )?warrant|no warrant(?:y|ies)\b",
        )
        if as_is:
            return "MISSING", self._quote(as_is)
        warranty = self._find(sentences, r"\bseller\b.{0,60}\bwarrants?\b|\bwarrants? that\b")
        if warranty:
            return "PRESENT", self._quote(warranty)
        return "MISSING", "No warranty about the condition of the goods found."

    def _check_clear_title_warranty(self, sentences, text_lower):
        clean = self._find(
            sentences,
            r"free (?:and clear )?(?:of|from) (?:all |any )?(?:liens?|encumbrances?|security interests?)|good (?:and marketable )?title",
        )
        if clean:
            return "PRESENT", self._quote(clean)
        conveys = self._find(sentences, r"\b(?:shall|will|agrees to)\b.{0,20}\b(?:convey|transfer)\w*\b.{0,30}\btitle\b")
        if conveys:
            return "MISSING", self._quote(conveys)
        return "MISSING", "No promise that the goods are free of liens or other claims found."

    def _check_inspection_rejection_right(self, sentences, text_lower):
        both = self._find(sentences, r"\binspect\w*\b.{0,120}\b(?:reject|refuse|cancel|return)\w*|\b(?:reject|refuse)\w*\b.{0,120}\binspect")
        if both:
            return "PRESENT", self._quote(both)
        inspect = self._find(sentences, r"\binspect\w*")
        if inspect:
            return "VAGUE", self._quote(inspect)
        return "MISSING", "No right for the Buyer to inspect the goods or reject them found."

    def _check_risk_of_loss(self, sentences, text_lower):
        return self._present_if(
            sentences,
            r"risk of (?:loss|damage)",
            "The contract does not say who bears the loss if the goods are damaged before delivery.",
        )

    def _check_deposit_refund(self, sentences, text_lower):
        deposit = self._find(sentences, r"down[\s-]?payment|\bdeposit\b|\badvance (?:payment|amount)\b|earnest money")
        if not deposit:
            return None  # nothing is paid before delivery
        refund = self._find(sentences, r"\b(?:refund|return(?:ed)? (?:of )?(?:the|all|any) (?:down[\s-]?payment|deposit|amounts?))")
        if refund:
            return "PRESENT", self._quote(refund)
        return "MISSING", self._quote(deposit)

    def _check_seller_default_remedy(self, sentences, text_lower):
        remedy = self._find(
            sentences,
            r"\bseller\b.{0,60}\b(?:fails?|failure|unable)\b.{0,60}\bdeliver|specific performance"
            r"|\bbuyer\b.{0,40}\bmay\b.{0,40}\b(?:cancel|terminate|rescind)",
        )
        if remedy:
            return "PRESENT", self._quote(remedy)
        return "MISSING", "No remedy for the Buyer if the Seller does not deliver found."

    def _check_governing_law(self, sentences, text_lower):
        law = self._find(sentences, r"governed by|laws? of the (?:state|country|republic)|governing law")
        if not law:
            return "MISSING", "No governing law or dispute forum found."
        # A template can name the clause but leave the place blank
        if re.search(r"_{3,}", law):
            return "VAGUE", self._quote(law)
        return "PRESENT", self._quote(law)
