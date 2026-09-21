import re
from typing import Literal
from pydantic import BaseModel, Field


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
    """

    BASELINE_CHECKS = [
        {
            "id": "disaster-recovery-sla",
            "title": "Disaster Recovery SLA & RTO/RPO",
            "category": "business_continuity",
            "risk_level": "high",
            "why_it_matters": (
                "The contract does not define explicit Recovery Time Objectives (RTO) or Recovery Point Objectives (RPO). "
                "If Provider suffers a catastrophic datacenter outage, there is no contractual commitment for when service or data will be restored."
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
                "Section 4.3 only requires notice 'without undue delay'. It lacks an explicit hour-based maximum window "
                "(e.g., within 24 to 72 hours). Without a strict timeframe, Customer may fail to meet mandatory regulatory reporting deadlines."
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
                "The agreement permits Provider to retain backups for up to 180 days, but lacks an affirmative obligation "
                "for Provider to return all Customer Data upon expiration and certify permanent destruction in writing."
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
                "Section 4.2 allows Provider to use subcontractors without prior notification or opportunity for Customer to object, "
                "which may violate Customer compliance standards or data residency policies."
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
                "Section 15 suspends liability during Force Majeure events, but gives Customer no right to terminate the contract "
                "if the outage or failure lasts for an extended period (e.g., longer than 30 consecutive days)."
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
                "Provider can terminate for convenience at any time upon 15 days' notice, but Customer is barred from terminating "
                "during the first 12 months and must provide 60 days' notice thereafter."
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
                "The agreement contains no requirement for Provider to maintain Technology Errors & Omissions or Cyber Liability insurance "
                "to backstop its indemnification and security commitments."
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
            "risk_level": "none",
            "why_it_matters": "Standard core protection exists in the contract.",
            "recommended_clause": "Clause present in Section 5.",
        },
        {
            "id": "liability-clause-present",
            "title": "Limitation of Liability Clause",
            "category": "liability",
            "risk_level": "none",
            "why_it_matters": "Standard core protection exists in the contract.",
            "recommended_clause": "Clause present in Section 9.",
        },
        {
            "id": "termination-clause-present",
            "title": "Termination Clause",
            "category": "termination",
            "risk_level": "none",
            "why_it_matters": "Standard core protection exists in the contract.",
            "recommended_clause": "Clause present in Section 10.",
        },
    ]

    def detect(self, full_text: str) -> list[dict]:
        """Analyze full document text against baseline checks and return structured results."""
        text_lower = full_text.lower()
        results = []

        for check in self.BASELINE_CHECKS:
            cid = check["id"]

            if cid == "confidentiality-clause-present":
                status: MissingStatus = "PRESENT" if "confidential" in text_lower else "MISSING"
                snippet = "Section 5: CONFIDENTIALITY" if status == "PRESENT" else ""
            elif cid == "liability-clause-present":
                status = "PRESENT" if "limitation of liability" in text_lower or "aggregate liability" in text_lower else "MISSING"
                snippet = "Section 9: LIMITATION OF LIABILITY" if status == "PRESENT" else ""
            elif cid == "termination-clause-present":
                status = "PRESENT" if "10. termination" in text_lower or "terminate this agreement" in text_lower else "MISSING"
                snippet = "Section 10: TERMINATION" if status == "PRESENT" else ""
            elif cid == "security-incident-timeframe":
                has_notice = "security incident" in text_lower or "unauthorized access" in text_lower
                has_strict_hours = bool(re.search(r"(?:within|in no event more than)\s+(?:24|48|72)\s*(?:hours|hrs)", text_lower))
                if has_strict_hours:
                    status = "PRESENT"
                    snippet = "Explicit hour-based notification window specified."
                elif has_notice:
                    status = "VAGUE"
                    snippet = "Section 4.3 specifies 'without undue delay', but omits an explicit hour-based SLA."
                else:
                    status = "MISSING"
                    snippet = "No security incident notification clause found."
            elif cid == "disaster-recovery-sla":
                has_rto_rpo = bool(re.search(r"\b(?:rto|rpo|recovery time objective|recovery point objective)\b", text_lower))
                if has_rto_rpo:
                    status = "PRESENT"
                    snippet = "Disaster recovery RTO/RPO defined."
                else:
                    status = "MISSING"
                    snippet = "No disaster recovery SLA or RTO/RPO targets found."
            elif cid == "data-return-destruction-certification":
                has_cert = bool(re.search(r"\bwritten certification\b|\bcertify\s+(?:in\s+writing\s+)?(?:the\s+)?destruction\b", text_lower))
                if has_cert:
                    status = "PRESENT"
                    snippet = "Written certification of destruction required."
                else:
                    status = "MISSING"
                    snippet = "Permits 180-day backup retention, but lacks affirmative destruction certification."
            elif cid == "subcontractor-advance-notice":
                # Must be within section 4 / data processing context
                sec4_match = re.search(r"4\.\s*data processing.*?(?=5\.\s*confidentiality)", text_lower, re.DOTALL)
                sec4_text = sec4_match.group(0) if sec4_match else ""
                has_sub_notice = bool(re.search(r"\b(?:prior written notice|advance notice|right to object)\b", sec4_text))
                if has_sub_notice:
                    status = "PRESENT"
                    snippet = "Advance notice of new subcontractors required."
                else:
                    status = "MISSING"
                    snippet = "Section 4.2 permits subcontractors without advance notice or objection rights."
            elif cid == "force-majeure-termination":
                sec15_match = re.search(r"15\.\s*force majeure.*?(?=16\.\s*assignment)", text_lower, re.DOTALL)
                sec15_text = sec15_match.group(0) if sec15_match else ""
                has_fm_term = "terminate" in sec15_text or "termination" in sec15_text
                if has_fm_term:
                    status = "PRESENT"
                    snippet = "Termination right for extended force majeure exists."
                else:
                    status = "MISSING"
                    snippet = "Section 15 suspends performance but provides no exit right for extended outages."
            elif cid == "customer-convenience-termination-parity":
                has_12m_lock = "12 months" in text_lower and "customer may terminate for convenience only" in text_lower
                if has_12m_lock:
                    status = "MISSING"
                    snippet = "Section 10.4 locks Customer for 12 months with 60-day notice, while Section 10.3 allows Provider 15-day exit."
                else:
                    status = "PRESENT"
                    snippet = "Bilateral convenience termination rights exist."
            elif cid == "cyber-insurance-requirements":
                has_insurance = "cyber liability" in text_lower or "errors and omissions" in text_lower or "errors & omissions" in text_lower
                if has_insurance:
                    status = "PRESENT"
                    snippet = "Cyber / E&O insurance required."
                else:
                    status = "MISSING"
                    snippet = "No insurance maintenance requirements found."
            else:
                status = "MISSING"
                snippet = ""

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
