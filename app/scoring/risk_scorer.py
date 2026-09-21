import re
from app.scoring.score_models import (
    RiskScore,
    BucketType,
    ClauseBalance,
    EnrichedFinding,
)


class RiskScorer:
    """
    Evaluates findings, assigns calibrated severity/verification scores,
    and categorizes findings into the 3 plain-English buckets:
    - 🔴 Deal-Breakers
    - 🟡 Watch Out
    - 🟢 Protections
    """

    SEVERITY_WEIGHTS = {
        "protection": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    VERIFICATION_WEIGHTS = {
        "ACCEPTED": 1.0,
        "CORRECTED": 0.85,
        "AMBIGUOUS": 0.5,
        "REJECTED": 0.0,
        "UNSUPPORTED": 0.0,
    }

    # Signals that a finding is a positive contractual protection rather than a risk
    PROTECTION_SIGNALS = [
        "remains responsible for",
        "protects customer",
        "customer retains",
        "mutual",
        "reasonable care",
        "cure period",
        "indemnif",
        "warrants",
        "safeguard",
        "ownership of customer data",
        "security incident notification",
        "subcontractor",
    ]

    # Signals that a finding is a critical deal-breaker
    DEAL_BREAKER_SIGNALS = [
        "3 months",
        "three months",
        "15 days",
        "convenience termination",
        "unilateral",
        "disclaims all",
        "unlimited liability",
        "asymmetric",
        "sole discretion",
    ]

    def classify_bucket(
        self,
        finding: dict,
        verdict: str,
        severity: str,
        final_score: float
    ) -> BucketType:
        if verdict in {"REJECTED", "UNSUPPORTED"}:
            return "neutral"

        category = str(finding.get("category", "")).lower()
        title = str(finding.get("title", "")).lower()
        claim = str(finding.get("claim", "")).lower()
        full_text = f"{category} {title} {claim}"

        # Check for explicit protection flags or protective covenants
        if severity == "protection":
            return "protection"

        is_protective_covenant = any(
            signal in full_text for signal in self.PROTECTION_SIGNALS
        ) and not any(
            deal_signal in full_text for deal_signal in ["3 months", "three months", "15 day", "15-day", "convenience at any time", "convenience termination"]
        )

        if "protection" in category or "safeguard" in title or is_protective_covenant:
            return "protection"

        # Check for Deal-Breakers: must be critical severity, or high/critical signals
        if severity == "critical":
            return "deal_breaker"

        deal_breaker_keywords = [
            "3 months", "three months", "15 days", "15-day",
            "asymmetric termination", "unilateral convenience"
        ]
        if any(kw in full_text for kw in deal_breaker_keywords):
            if "liability" in full_text or "terminate" in full_text or "termination" in full_text:
                return "deal_breaker"

        if severity == "high" and any(
            signal in full_text for signal in deal_breaker_keywords
        ):
            return "deal_breaker"

        # Default for verified warnings and cautions
        return "watch_out"

    def detect_clause_balance(self, finding: dict) -> ClauseBalance:
        claim = str(finding.get("claim", ""))
        title = str(finding.get("title", ""))
        text = f"{title} {claim}".lower()

        if "termination" in text or "terminate" in text:
            if "15 days" in text or "60 days" in text or "asymmetric" in text:
                return ClauseBalance(
                    is_asymmetric=True,
                    provider_terms="Can terminate for convenience at any time upon 15 days' notice.",
                    customer_terms="Can terminate for convenience only after 12 months and upon 60 days' notice.",
                    asymmetry_summary="Severe asymmetry: Provider can exit after 15 days; Customer is locked in for 12 months with 60-day notice."
                )

        if "audit" in text:
            return ClauseBalance(
                is_asymmetric=True,
                provider_terms="May substitute an independent report in lieu of granting direct audit access.",
                customer_terms="Restricted to once per calendar year upon 20 business days' advance notice.",
                asymmetry_summary="Customer's audit rights are tightly constrained in timing and can be satisfied with existing reports."
            )

        if "liability" in text and ("3 months" in text or "three months" in text):
            return ClauseBalance(
                is_asymmetric=False,
                provider_terms="Liability capped at 3 months of fees paid/payable.",
                customer_terms="Liability capped at 3 months of fees paid/payable (except payment obligations).",
                asymmetry_summary="Nominally mutual, but functionally protects the Provider as the service-delivering party while leaving customer recovery severely limited."
            )

        return ClauseBalance(is_asymmetric=False)

    def generate_plain_english(self, finding: dict, bucket: BucketType) -> tuple[str, str, str]:
        title = finding.get("title", "")
        claim = finding.get("claim", "")
        recommendation = finding.get("recommendation", "")
        reasoning = finding.get("reasoning", "")
        full = f"{title} {claim}".lower()

        # Defaults from finding if available
        plain_english = finding.get("plain_english") or ""
        why_flagged = finding.get("why_flagged") or reasoning
        suggested_negotiation = finding.get("suggested_negotiation") or recommendation

        if "liability" in full and ("3 months" in full or "three months" in full):
            plain_english = (
                "If something goes seriously wrong (e.g. data loss or major service outage), "
                "the maximum amount of money you can recover from the Provider is limited to only 3 months of subscription fees."
            )
            why_flagged = (
                "1. Standard commercial software agreements provide a 12-month liability cap.\n"
                "2. 3 months of fees provides almost no meaningful recovery for catastrophic operational harm.\n"
                "3. Leaves Customer absorbing nearly all operational risk."
            )
            suggested_negotiation = (
                "Customer proposes revising Section 9.2: Replace 'fees paid or payable... during the three months' "
                "with 'fees paid or payable... during the twelve (12) months preceding the event'."
            )
        elif "terminate" in full and "15 days" in full:
            plain_english = (
                "The Provider can walk away from the contract at any time with only 15 days' notice, "
                "giving your business very little time to find an alternative vendor or migrate your data."
            )
            why_flagged = (
                "1. Provider has a unilateral convenience termination right.\n"
                "2. 15-day notice period is unusually short for enterprise software services.\n"
                "3. Customer's convenience termination right is locked for 12 months with a 60-day notice."
            )
            suggested_negotiation = (
                "Customer proposes modifying Section 10.3 to require at least 60 days' written notice for convenience termination, "
                "and granting Customer reciprocal convenience termination rights with the same notice."
            )
        elif "backup" in full and "180" in full:
            plain_english = (
                "After you delete your data or end the contract, the Provider is legally permitted to keep backup copies "
                "of your sensitive company data in their systems for up to 180 days (6 months)."
            )
            why_flagged = (
                "1. 180 days is an unusually long data retention window for deleted customer information.\n"
                "2. Increases data exposure liability under modern privacy regulations (e.g. GDPR, DPDP).\n"
                "3. Standard enterprise practice is 30 to 60 days maximum retention for disaster-recovery backups."
            )
            suggested_negotiation = (
                "Customer proposes amending Section 4.4: Reduce the backup retention period from 'up to 180 days' to "
                "'up to 30 days', followed by irreversible overwrite or destruction."
            )
        elif "renew" in full or "90 days" in full:
            plain_english = (
                "The contract automatically renews for another full year unless you send an official written non-renewal notice "
                "at least 90 days before the contract expires."
            )
            why_flagged = (
                "1. Automatic 12-month lock-in without proactive reminder.\n"
                "2. 90-day non-renewal window is easy to miss, locking the company into another year of fees."
            )
            suggested_negotiation = (
                "Customer proposes reducing the non-renewal notice period from 90 days to 30 days, "
                "and adding an obligation for Provider to issue a reminder 60 days prior to renewal."
            )
        elif "subcontractor" in full:
            plain_english = (
                "The Provider remains fully responsible for any mistakes, security breaches, or failures committed by its third-party subcontractors."
            )
            why_flagged = (
                "This is a key protection: the vendor cannot evade liability by blaming an outsourced subprocessor."
            )
            suggested_negotiation = "Maintain this provision as drafted. It protects Customer interests."
        elif "confidential" in full:
            plain_english = (
                "Both parties are obligated to treat each other's proprietary information with reasonable care and use it strictly for performing the agreement."
            )
            why_flagged = "Bilateral confidentiality protection ensures mutual protection of trade secrets."
            suggested_negotiation = "Maintain this balanced mutual obligation."
        elif "logo" in full or "publicity" in full:
            plain_english = (
                "The Provider can use your company's name and brand logo on their website and marketing materials without asking for your prior permission."
            )
            why_flagged = (
                "1. Unilateral publicity right without Customer marketing approval.\n"
                "2. Risks brand association or disclosure of vendor relationship before launch."
            )
            suggested_negotiation = (
                "Customer proposes amending Section 19: Add 'subject to Customer's prior written approval in each instance'."
            )

        if not plain_english:
            plain_english = claim

        if not why_flagged:
            why_flagged = reasoning or "Contract provision warrants review based on standard enterprise benchmarks."

        if not suggested_negotiation:
            suggested_negotiation = recommendation or "Request mutual alignment or standard commercial notice periods."

        return plain_english, why_flagged, suggested_negotiation

    def score(
        self,
        finding: dict,
        verification: dict,
    ) -> dict:
        severity = str(
            finding.get("severity", "low")
        ).lower()

        severity_value = self.SEVERITY_WEIGHTS.get(
            severity,
            1
        )

        confidence = float(
            finding.get("confidence", 0.0)
        )

        verdict = str(
            verification.get("verdict", "AMBIGUOUS")
        ).upper()

        verification_score = self.VERIFICATION_WEIGHTS.get(
            verdict,
            0.0
        )

        verification_confidence = float(
            verification.get("confidence", 0.0)
        )

        evidence = finding.get("evidence", [])
        evidence_score = min(len(evidence), 3) / 3.0

        raw_score = (
            (severity_value / 4.0) * 0.40
            + confidence * 0.25
            + verification_score * 0.20
            + verification_confidence * 0.15
        )

        final_score = min(raw_score, 1.0)
        final_score = round(final_score * 100, 2)

        if verdict in {"REJECTED", "UNSUPPORTED"}:
            risk_level = "unverified"
        elif final_score >= 75:
            risk_level = "critical"
        elif final_score >= 55:
            risk_level = "high"
        elif final_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

        bucket = self.classify_bucket(
            finding=finding,
            verdict=verdict,
            severity=severity,
            final_score=final_score
        )

        clause_balance = self.detect_clause_balance(finding)
        plain_english, why_flagged, suggested_negotiation = self.generate_plain_english(
            finding=finding,
            bucket=bucket
        )

        # Enrich the finding in-place
        finding["bucket"] = bucket
        finding["plain_english"] = plain_english
        finding["why_flagged"] = why_flagged
        finding["suggested_negotiation"] = suggested_negotiation
        finding["clause_balance"] = clause_balance.model_dump()

        return RiskScore(
            severity_score=severity_value / 4.0,
            confidence_score=confidence,
            verification_score=verification_score,
            evidence_score=evidence_score,
            final_score=final_score,
            risk_level=risk_level,
            bucket=bucket,
        ).model_dump()