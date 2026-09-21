from pathlib import Path


class MarkdownExporter:
    """
    Exports executive-ready, boardroom-grade Markdown Audit Memos.
    """

    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, report_data: dict, filename: str | None = None) -> Path:
        doc_name = report_data.get("document_name", "audit_report")
        clean_name = Path(doc_name).stem

        if filename:
            file_path = self.output_dir / filename
        else:
            file_path = self.output_dir / f"{clean_name}_audit_memo.md"

        md_content = self.generate_markdown(report_data)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return file_path

    def generate_markdown(self, report: dict) -> str:
        doc = report.get("document_name", "Contract")
        parties = report.get("parties", {})
        customer = parties.get("customer", "Customer")
        provider = parties.get("provider", "Provider")

        health = report.get("health", {})
        score = health.get("health_score", 100.0)
        rating = health.get("rating", "Strong")
        headline = health.get("headline", "")

        deal_breakers = health.get("deal_breakers", [])
        watch_out = health.get("watch_out", [])
        protections = health.get("protections", [])
        missing_clauses = report.get("missing_clauses", [])
        clause_balance = report.get("clause_balance", [])
        obligations = report.get("obligations", {})
        tables = report.get("tables", [])
        sig_status = report.get("signature_status", {})

        md = []

        # Header
        md.append(f"# 🛡️ Enterprise Contract Audit Memo")
        md.append(f"**Document:** `{doc}`  ")
        md.append(f"**Customer:** {customer} | **Provider:** {provider}  ")
        md.append("")
        md.append("---")
        md.append("")

        # 1. Health Score Dashboard
        md.append(f"## 1. 🛡️ Contract Health Dashboard")
        md.append("")
        md.append(f"```text")
        md.append(f"┌──────────────────────────────────────────────────────────────┐")
        md.append(f"│  CONTRACT HEALTH SCORE                                       │")
        md.append(f"│                                                              │")
        md.append(f"│             ┌──────────────┐                                 │")
        md.append(f"│             │    {score:4.1f}      │   Rating: {rating:<15}       │")
        md.append(f"│             │   / 100      │                                 │")
        md.append(f"│             │   HEALTH     │                                 │")
        md.append(f"│             └──────────────┘                                 │")
        md.append(f"│                                                              │")
        md.append(f"│  🔴 {len(deal_breakers)} Deal-Breakers    🟡 {len(watch_out)} Watch Out    🟢 {len(protections)} Protections   │")
        md.append(f"└──────────────────────────────────────────────────────────────┘")
        md.append(f"```")
        md.append(f"> **Summary:** {headline}")
        md.append("")

        # 2. Deal-Breakers
        md.append(f"## 2. 🔴 Deal-Breakers ({len(deal_breakers)})")
        if not deal_breakers:
            md.append("✓ No critical deal-breakers identified.")
        else:
            for idx, db in enumerate(deal_breakers, start=1):
                title = db.get("title", "Critical Risk")
                plain = db.get("plain_english", "")
                why = db.get("why_flagged", "")
                remedy = db.get("suggested_negotiation", "")
                evidence = db.get("evidence", [])
                page = evidence[0].get("page", "?") if evidence else "?"
                quote = evidence[0].get("quote", "") if evidence else ""

                md.append(f"### {idx}. {title}")
                md.append(f"📖 **In Plain English:**  ")
                md.append(f"> {plain}")
                md.append("")
                md.append(f"⚠️ **Why It Matters:**  ")
                for line in why.split("\n"):
                    if line.strip():
                        md.append(f"- {line.strip()}")
                md.append("")
                md.append(f"📄 **Contract Evidence (Page {page}):**  ")
                md.append(f"> \"{quote}\"")
                md.append("")
                md.append(f"💡 **Suggested Negotiation Remedy:**  ")
                md.append(f"```text\n{remedy}\n```")
                md.append("")

        # 3. Watch Out
        md.append(f"## 3. 🟡 Watch Out ({len(watch_out)})")
        if not watch_out:
            md.append("✓ No secondary cautions identified.")
        else:
            for idx, wo in enumerate(watch_out, start=1):
                title = wo.get("title", "")
                plain = wo.get("plain_english", "")
                why = wo.get("why_flagged", "")
                remedy = wo.get("suggested_negotiation", "")
                evidence = wo.get("evidence", [])
                page = evidence[0].get("page", "?") if evidence else "?"
                quote = evidence[0].get("quote", "") if evidence else ""

                md.append(f"#### {idx}. {title}")
                md.append(f"- **Impact:** {plain}")
                md.append(f"- **Evidence (p. {page}):** \"{quote}\"")
                if remedy:
                    md.append(f"- **Recommended Fix:** {remedy}")
                md.append("")

        # 4. Protections
        md.append(f"## 4. 🟢 Active Protections ({len(protections)})")
        if not protections:
            md.append("No explicit protective covenants detected.")
        else:
            for p in protections:
                title = p.get("title", "")
                plain = p.get("plain_english", "")
                evidence = p.get("evidence", [])
                page = evidence[0].get("page", "?") if evidence else "?"
                quote = evidence[0].get("quote", "") if evidence else ""
                md.append(f"- ✓ **{title}**: {plain} *(Page {page}: \"{quote}\")*")
        md.append("")

        # 5. What's Missing?
        md.append(f"## 5. ⚠️ What's Missing? (Protective Baseline Gap Analysis)")
        md.append("| Status | Protection Requirement | Risk Impact | Recommended Action |")
        md.append("| :--- | :--- | :--- | :--- |")
        for m in missing_clauses:
            status_icon = "⚠️ MISSING" if m.get("status") == "MISSING" else ("⚠️ VAGUE" if m.get("status") == "VAGUE" else "✓ PRESENT")
            title = m.get("title", "")
            risk = m.get("risk_level", "none").upper()
            why = m.get("why_it_matters", "").replace("|", "-")
            md.append(f"| {status_icon} | **{title}** | {risk} | {why[:100]}... |")
        md.append("")

        # 6. Clause Balance / Asymmetry
        if clause_balance:
            md.append(f"## 6. ⚖️ Clause Balance & Asymmetry Analysis")
            for cb in clause_balance:
                md.append(f"### {cb.get('title')}")
                md.append(f"> **Asymmetry:** {cb.get('asymmetry_summary')}")
                md.append(f"- **Provider Terms:** {cb.get('provider_terms')}")
                md.append(f"- **Customer Terms:** {cb.get('customer_terms')}")
                md.append("")

        # 7. Obligations & Timeline
        timeline = obligations.get("timeline", [])
        if timeline:
            md.append(f"## 7. 📅 Obligations & Deadlines Timeline")
            md.append("```text")
            md.append("TIMELINE")
            for t in timeline:
                period = t.get("period_label") if isinstance(t, dict) else getattr(t, "period_label", "")
                party = t.get("party") if isinstance(t, dict) else getattr(t, "party", "")
                action = t.get("action") if isinstance(t, dict) else getattr(t, "action", "")
                md.append(f"  ├── {period:<22} [{party}] {action}")
            md.append("```")
            md.append("")

        # 8. Tables & Pricing
        if tables:
            md.append(f"## 8. 📊 Structured Tables & Pricing Analysis")
            for t in tables:
                table_id = t.get("table_id") if isinstance(t, dict) else getattr(t, "table_id", "")
                page = t.get("page_number") if isinstance(t, dict) else getattr(t, "page_number", "")
                ttype = t.get("table_type") if isinstance(t, dict) else getattr(t, "table_type", "")
                md_repr = t.get("markdown") if isinstance(t, dict) else getattr(t, "markdown", "")
                risks = t.get("risks", []) if isinstance(t, dict) else getattr(t, "risks", [])

                md.append(f"### Table {table_id} (Page {page}, Type: `{ttype}`)")
                md.append(md_repr)
                md.append("")
                if risks:
                    md.append(f"**Identified Table Risks:**")
                    for r in risks:
                        rtitle = r.get("risk_title") if isinstance(r, dict) else getattr(r, "risk_title", "")
                        obs = r.get("observation") if isinstance(r, dict) else getattr(r, "observation", "")
                        rec = r.get("recommendation") if isinstance(r, dict) else getattr(r, "recommendation", "")
                        md.append(f"- ⚠️ **{rtitle}**: {obs}")
                        md.append(f"  - *Remedy:* {rec}")
                    md.append("")

        # 9. Signatures & Execution
        if sig_status:
            md.append(f"## 9. ✍️ Visual Scanner: Signature & Execution Status")
            headline = sig_status.get("headline", "")
            notes = sig_status.get("visual_notes", "")
            disclaimer = sig_status.get("disclaimer", "")
            md.append(f"> **{headline}**")
            md.append(f"*{notes}*")
            md.append("")
            parties_list = sig_status.get("parties", [])
            for p in parties_list:
                prole = p.get("party_role") if isinstance(p, dict) else getattr(p, "party_role", "")
                pname = p.get("party_name") if isinstance(p, dict) else getattr(p, "party_name", "")
                pstat = p.get("status_label") if isinstance(p, dict) else getattr(p, "status_label", "")
                md.append(f"- **{prole} ({pname}):** `{pstat}`")
            md.append("")
            md.append(f"> *Note: {disclaimer}*")
            md.append("")

        md.append("---")
        md.append("*Report generated by Enterprise Auditor 2.0*")

        return "\n".join(md)
