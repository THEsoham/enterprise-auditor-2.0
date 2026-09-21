from typing import Optional


class ReportBuilder:
    """
    Compiles an enterprise audit package combining:
    - 100-point Contract Health Score
    - 3 Plain-English Buckets (🔴 Deal-Breakers, 🟡 Watch Out, 🟢 Protections)
    - What's Missing? Baseline Protections Check
    - Clause Balance & Asymmetry Analysis
    - Obligations & Deadlines Timeline Map
    - Extracted Tables & Pricing Risk Analysis
    - Signature & Visual Execution Analysis
    - Real Grounded Knowledge Graph
    - AI Courtroom Debate Histories
    """

    def build(
        self,
        document_name: str,
        findings: list[dict],
        risk_scores: list[dict],
        health_score: dict,
        debate_histories: Optional[list[list[dict]]] = None,
        missing_clauses: Optional[list[dict]] = None,
        obligations: Optional[dict] = None,
        tables: Optional[list[dict]] = None,
        signature_status: Optional[dict] = None,
        graph_data: Optional[dict] = None,
        parties: Optional[dict] = None,
    ) -> dict:
        debate_histories = debate_histories or []
        missing_clauses = missing_clauses or []
        tables = tables or []
        parties = parties or {
            "customer": "Customer",
            "provider": "Provider",
        }

        # Extract asymmetric clause findings for Clause Balance view
        clause_balance_items = []
        for finding in findings:
            cb = finding.get("clause_balance")
            if cb and cb.get("is_asymmetric"):
                clause_balance_items.append({
                    "title": finding.get("title", ""),
                    "provider_terms": cb.get("provider_terms", ""),
                    "customer_terms": cb.get("customer_terms", ""),
                    "asymmetry_summary": cb.get("asymmetry_summary", ""),
                    "page": finding.get("evidence", [{}])[0].get("page"),
                })

        enriched_findings_list = []
        for index, finding in enumerate(findings):
            score_data = risk_scores[index] if index < len(risk_scores) else {}
            history = debate_histories[index] if index < len(debate_histories) else []

            enriched_findings_list.append({
                "finding_id": f"finding-{index+1:03d}",
                "title": finding.get("title", ""),
                "category": finding.get("category", ""),
                "severity": finding.get("severity", ""),
                "bucket": finding.get("bucket") or score_data.get("bucket", "watch_out"),
                "claim": finding.get("claim", ""),
                "plain_english": finding.get("plain_english", finding.get("claim", "")),
                "why_flagged": finding.get("why_flagged", finding.get("reasoning", "")),
                "suggested_negotiation": finding.get("suggested_negotiation", finding.get("recommendation", "")),
                "clause_balance": finding.get("clause_balance"),
                "confidence": finding.get("confidence", 0.0),
                "evidence": finding.get("evidence", []),
                "risk_score": score_data,
                "debate_history": history,
            })

        return {
            "document_name": document_name,
            "parties": parties,
            "health": health_score,
            "summary": {
                "health_score": health_score.get("health_score", 100.0),
                "rating": health_score.get("rating", "Strong"),
                "headline": health_score.get("headline", ""),
                "deal_breakers_count": health_score.get("deal_breakers_count", 0),
                "watch_out_count": health_score.get("watch_out_count", 0),
                "protections_count": health_score.get("protections_count", 0),
                "missing_protections_count": health_score.get("missing_protections_count", 0),
                "total_verified_findings": len(findings),
            },
            "findings": enriched_findings_list,
            "missing_clauses": missing_clauses,
            "clause_balance": clause_balance_items,
            "obligations": obligations or {},
            "tables": tables,
            "signature_status": signature_status or {},
            "graph": graph_data or {},
        }