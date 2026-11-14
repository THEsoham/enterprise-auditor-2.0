class HealthScore:
    """
    Computes a transparent 100-point Contract Health Score
    and organizes verified findings into the 3 plain-English buckets:
    - 🔴 Deal-Breakers
    - 🟡 Watch Out
    - 🟢 Protections
    """

    DEAL_BREAKER_PENALTY = 8.0
    WATCH_OUT_PENALTY = 3.0
    MISSING_PROTECTION_PENALTY = 2.0
    ACTIVE_PROTECTION_REWARD = 2.5
    # A missing protection costs more the more it matters; unlabelled ones cost the default
    MISSING_PENALTY_BY_RISK = {"critical": 5.0, "high": 3.0, "medium": 2.0, "low": 1.0}
    MAX_MISSING_DEDUCTION = 20.0
    # An unfilled template's key terms (price, parties, dates) are blank, so it cannot rate well
    TEMPLATE_SCORE_CAP = 60.0

    def calculate(
        self,
        findings: list[dict],
        risk_scores: list[dict],
        missing_clauses: list[dict] | None = None,
        profile: dict | None = None,
    ) -> dict:
        missing_clauses = missing_clauses or []
        profile = profile or {}
        warnings: list[str] = []

        deal_breakers = []
        watch_out = []
        protections = []

        for idx, finding in enumerate(findings):
            score_data = risk_scores[idx] if idx < len(risk_scores) else {}
            bucket = score_data.get("bucket") or finding.get("bucket", "watch_out")
            risk_level = score_data.get("risk_level", "medium")

            if risk_level == "unverified":
                continue

            item = {
                "title": finding.get("title", ""),
                "category": finding.get("category", ""),
                "claim": finding.get("claim", ""),
                "plain_english": finding.get("plain_english", finding.get("claim", "")),
                "why_flagged": finding.get("why_flagged", finding.get("reasoning", "")),
                "suggested_negotiation": finding.get("suggested_negotiation", finding.get("recommendation", "")),
                "clause_balance": finding.get("clause_balance"),
                "evidence": finding.get("evidence", []),
                "severity": finding.get("severity", "medium"),
                "bucket": bucket,
                "confidence": finding.get("confidence", 0.0),
            }

            if bucket == "deal_breaker":
                deal_breakers.append(item)
            elif bucket == "protection":
                protections.append(item)
            else:
                watch_out.append(item)

        # Count critical missing protections
        critical_missing = [
            m for m in missing_clauses
            if str(m.get("status", "")).upper() in {"MISSING", "VAGUE"}
        ]
        missing_count = len(critical_missing)

        # Transparent 100-point health calculation
        base_score = 100.0
        deal_breaker_deductions = len(deal_breakers) * self.DEAL_BREAKER_PENALTY
        watch_out_deductions = len(watch_out) * self.WATCH_OUT_PENALTY
        missing_deductions = min(
            sum(
                self.MISSING_PENALTY_BY_RISK.get(str(m.get("risk_level", "")).lower(), self.MISSING_PROTECTION_PENALTY)
                for m in critical_missing
            ),
            self.MAX_MISSING_DEDUCTION,
        )
        protection_bonus = min(len(protections) * self.ACTIVE_PROTECTION_REWARD, 15.0)

        total_deductions = deal_breaker_deductions + watch_out_deductions + missing_deductions
        computed_health = base_score - total_deductions + protection_bonus
        final_health = round(max(0.0, min(100.0, computed_health)), 1)

        if final_health >= 85:
            rating = "Strong"
        elif final_health >= 65:
            rating = "Moderate"
        elif final_health >= 45:
            rating = "High Risk"
        else:
            rating = "Critical"

        if profile.get("is_template"):
            blanks = profile.get("blank_fields", 0)
            examples = ", ".join(profile.get("blank_examples") or [])
            warnings.append(
                f"Unfilled template: {blanks} terms are left blank" + (f" ({examples})" if examples else "")
                + f". The score is capped at {int(self.TEMPLATE_SCORE_CAP)} until they are filled in."
            )
            if final_health > self.TEMPLATE_SCORE_CAP:
                final_health = self.TEMPLATE_SCORE_CAP
            rating = "Incomplete Draft" if rating in ("Strong", "Moderate") else rating

        headline = (
            f"Health Score: {final_health}/100 ({rating}) — "
            f"{len(deal_breakers)} Deal-Breakers, {len(watch_out)} Watch Out, {len(protections)} Protections"
        )

        if profile and profile.get("is_contract") is False:
            # Scoring a job description or a report as a contract would be meaningless
            final_health = None
            rating = "Not a Contract"
            headline = "Not a contract — this document has no binding terms between parties, so it was not scored"
            warnings.append(
                "This document does not read as a contract (no parties, recitals or binding 'shall' terms), "
                "so the contract checks were not run."
            )

        return {
            "health_score": final_health,
            "rating": rating,
            "headline": headline,
            "deal_breakers_count": len(deal_breakers),
            "watch_out_count": len(watch_out),
            "protections_count": len(protections),
            "missing_protections_count": missing_count,
            "warnings": warnings,
            "deal_breakers": deal_breakers,
            "watch_out": watch_out,
            "protections": protections,
            "score_breakdown": {
                "base_score": base_score,
                "deal_breaker_deductions": deal_breaker_deductions,
                "watch_out_deductions": watch_out_deductions,
                "missing_deductions": missing_deductions,
                "protection_rewards": protection_bonus,
            },
        }