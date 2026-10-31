from app.scoring.score_models import (
    RiskScore,
    BucketType,
    ClauseBalance,
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
        "UNVERIFIED": 0.0,
    }

    # Weights of the per-finding risk score (sum to 1.0)
    SCORE_WEIGHTS = {
        "severity": 0.35,
        "auditor_confidence": 0.20,
        "verdict": 0.20,
        "verifier_confidence": 0.15,
        "evidence": 0.10,
    }

    # Fallback signals, used only when the Auditor did not label finding_type
    PROTECTION_SIGNALS = [
        "remains responsible for",
        "protects customer",
        "customer retains",
        "reasonable care",
        "cure period",
        "warrants",
        "safeguard",
    ]

    # Wording that turns a high-severity risk into a deal-breaker
    DEAL_BREAKER_SIGNALS = [
        "unilateral",
        "sole discretion",
        "at any time",
        "for convenience",
        "unlimited liability",
        "disclaims all",
        "asymmetric",
        "without consent",
        "without approval",
    ]

    def classify_bucket(
        self,
        finding: dict,
        verdict: str,
        severity: str,
        final_score: float
    ) -> BucketType:
        if verdict in {"REJECTED", "UNSUPPORTED", "UNVERIFIED"}:
            return "neutral"

        finding_type = str(finding.get("finding_type", "")).lower()
        category = str(finding.get("category", "")).lower()
        title = str(finding.get("title", "")).lower()
        claim = str(finding.get("claim", "")).lower()
        full_text = f"{category} {title} {claim}"

        if severity == "protection" or finding_type == "protection":
            return "protection"

        if not finding_type and (
            "protection" in category
            or any(signal in full_text for signal in self.PROTECTION_SIGNALS)
        ):
            return "protection"

        if severity == "critical":
            return "deal_breaker"

        # Asymmetry alone is common; a high-severity finding also needs deal-breaker wording
        if severity == "high" and any(signal in full_text for signal in self.DEAL_BREAKER_SIGNALS):
            return "deal_breaker"

        return "watch_out"

    def detect_clause_balance(self, finding: dict) -> ClauseBalance:
        """Uses the Auditor's own clause-balance analysis of the quoted text."""
        raw = finding.get("clause_balance")
        if not isinstance(raw, dict):
            return ClauseBalance(is_asymmetric=False)

        return ClauseBalance(
            is_asymmetric=bool(raw.get("is_asymmetric", False)),
            provider_terms=str(raw.get("provider_terms") or ""),
            customer_terms=str(raw.get("customer_terms") or ""),
            asymmetry_summary=str(raw.get("asymmetry_summary") or ""),
        )

    def generate_plain_english(self, finding: dict, bucket: BucketType) -> tuple[str, str, str]:
        """Plain-English summary, why it was flagged, and a negotiation suggestion."""
        plain_english = str(finding.get("plain_english") or finding.get("claim") or "")
        why_flagged = str(
            finding.get("why_flagged")
            or finding.get("reasoning")
            or "Contract provision warrants review based on standard enterprise benchmarks."
        )

        if bucket == "protection":
            default_negotiation = "Keep this provision as drafted; it protects your position."
        else:
            default_negotiation = "Request mutual terms or standard commercial notice periods."

        suggested_negotiation = str(
            finding.get("suggested_negotiation")
            or finding.get("recommendation")
            or default_negotiation
        )

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

        try:
            confidence = float(finding.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        verdict = str(
            verification.get("verdict", "AMBIGUOUS")
        ).upper()

        verification_score = self.VERIFICATION_WEIGHTS.get(
            verdict,
            0.0
        )

        try:
            verification_confidence = float(verification.get("confidence", 0.0))
        except (TypeError, ValueError):
            verification_confidence = 0.0

        evidence = finding.get("evidence", [])
        evidence_score = min(len(evidence), 3) / 3.0

        w = self.SCORE_WEIGHTS
        raw_score = (
            (severity_value / 4.0) * w["severity"]
            + confidence * w["auditor_confidence"]
            + verification_score * w["verdict"]
            + verification_confidence * w["verifier_confidence"]
            + evidence_score * w["evidence"]
        )

        final_score = min(raw_score, 1.0)
        final_score = round(final_score * 100, 2)

        if verdict in {"REJECTED", "UNSUPPORTED", "UNVERIFIED"}:
            risk_level = "unverified"
        elif final_score >= 75:
            risk_level = "critical"
        elif final_score >= 55:
            risk_level = "high"
        elif final_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

        clause_balance = self.detect_clause_balance(finding)
        finding["clause_balance"] = clause_balance.model_dump()

        bucket = self.classify_bucket(
            finding=finding,
            verdict=verdict,
            severity=severity,
            final_score=final_score
        )

        plain_english, why_flagged, suggested_negotiation = self.generate_plain_english(
            finding=finding,
            bucket=bucket
        )

        # Enrich the finding in-place
        finding["bucket"] = bucket
        finding["plain_english"] = plain_english
        finding["why_flagged"] = why_flagged
        finding["suggested_negotiation"] = suggested_negotiation

        return RiskScore(
            severity_score=severity_value / 4.0,
            confidence_score=confidence,
            verification_score=verification_score,
            evidence_score=evidence_score,
            final_score=final_score,
            risk_level=risk_level,
            bucket=bucket,
        ).model_dump()
