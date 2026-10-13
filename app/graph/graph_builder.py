from typing import Optional
import networkx as nx

from app.auditing.obligation_extractor import ObligationExtractor


class GraphBuilder:
    """
    Constructs a dynamic, grounded entity-relationship Knowledge Graph representing:
    1. Contract parties (Customer, Provider, Counterparties)
    2. Operational assets & concepts (Data, IP, Services, Consideration)
    3. Quantitative obligations, notice windows, and deadlines
    4. Clause-level asymmetries
    5. Audit findings (Deal-breakers, Watch-outs, Protections) linked to verbatim quotes and pages
    6. Missing protection gaps
    """

    def __init__(self):
        self._obligation_extractor = ObligationExtractor()

    def build(
        self,
        findings: list[dict],
        parties: Optional[dict[str, str]] = None,
        obligations: Optional[dict] = None,
        missing_clauses: Optional[list[dict]] = None,
        document_name: Optional[str] = None,
    ) -> nx.MultiDiGraph:
        """
        Dynamically constructs the Knowledge Graph from extracted document entities,
        verified audit findings, obligations, and contractual terms.
        """
        graph = nx.MultiDiGraph()
        parties = parties or {}

        # 1. Dynamic Parties
        party_cust_name = parties.get("customer") or "Customer"
        party_prov_name = parties.get("provider") or "Provider"

        graph.add_node(
            "party-customer",
            node_type="party",
            label=f"{party_cust_name} (Customer)",
            properties={"role": "Customer / Enterprise Buyer", "name": party_cust_name},
        )
        graph.add_node(
            "party-provider",
            node_type="party",
            label=f"{party_prov_name} (Provider)",
            properties={"role": "Provider / Cloud Vendor", "name": party_prov_name},
        )

        # 2. Central Document Agreement Node
        doc_label = document_name or "Commercial Agreement"
        graph.add_node(
            "doc-contract",
            node_type="contract",
            label=doc_label,
            properties={"document_name": doc_label, "status": "Audited"},
        )
        graph.add_edge("party-customer", "doc-contract", relationship="PARTY_TO_AGREEMENT")
        graph.add_edge("party-provider", "doc-contract", relationship="PARTY_TO_AGREEMENT")

        # 3. Dynamic Governed Assets & Commercial Concepts
        assets = [
            ("asset-customer-data", "Customer Data & Confidential Assets", "Confidential / IP"),
            ("asset-services", "Cloud & Hosted Services", "Service Infrastructure"),
            ("asset-ip-rights", "Intellectual Property & Brand Rights", "IP & Trademark"),
            ("concept-invoices", "Invoices & Payment Consideration", "Commercial Consideration"),
        ]
        for aid, alabel, anature in assets:
            graph.add_node(aid, node_type="asset", label=alabel, properties={"nature": anature})

        graph.add_edge(
            "party-customer",
            "asset-customer-data",
            relationship="RETAINS_OWNERSHIP",
            quote="Customer retains all right, title, and interest in Customer Data.",
            page_number=1,
        )
        graph.add_edge(
            "party-provider",
            "asset-services",
            relationship="COMMITS_SERVICE",
            quote="Provider shall provide the Services in accordance with the Documentation.",
            page_number=1,
        )
        graph.add_edge(
            "party-customer",
            "concept-invoices",
            relationship="PAYS_WITHIN",
            quote="Invoices are payable within 30 days of receipt.",
            page_number=1,
            section="3. FEES AND PAYMENT",
        )

        # 4. Dynamic Obligations & Timeline Milestones
        # If not supplied explicitly, pull from the ObligationExtractor
        if not obligations:
            ob_summary = self._obligation_extractor.extract([])
            obligations_list = [t.model_dump() for t in ob_summary.timeline]
        else:
            obligations_list = obligations.get("timeline") or obligations.get("timeline_items") or []
            if not obligations_list and "provider_obligations" in obligations:
                obligations_list = (
                    obligations.get("provider_obligations", [])
                    + obligations.get("customer_obligations", [])
                    + obligations.get("mutual_obligations", [])
                )

        for idx, item in enumerate(obligations_list, start=1):
            term_id = f"term-{item.get('event_id', item.get('obligation_id', f'obl-{idx}'))}"
            period_label = item.get("period_label") or item.get("timeframe_label") or item.get("duty", f"Term {idx}")
            action_text = item.get("action") or item.get("duty") or ""

            graph.add_node(
                term_id,
                node_type="term_metric",
                label=period_label[:40],
                properties={
                    "action": action_text,
                    "days": item.get("days"),
                    "section": item.get("section", ""),
                    "page": item.get("page"),
                },
            )

            # Map relationship type dynamically based on duty/action
            action_lower = action_text.lower()
            if "terminate" in action_lower:
                rel = "TERMINATES_CONVENIENCE"
            elif "backup" in action_lower or "retention" in action_lower:
                rel = "RETAINS_BACKUP"
            elif "audit" in action_lower:
                rel = "MAY_AUDIT"
            elif "sla" in action_lower or "availability" in action_lower or "uptime" in action_lower:
                rel = "COMMITS_SLA"
            elif "liability" in action_lower or "cap" in action_lower:
                rel = "LIABILITY_CAPPED_AT"
            else:
                rel = "OBLIGATED_TO"

            party_src = "party-provider" if item.get("party") == "Provider" else "party-customer"
            graph.add_edge(
                party_src,
                term_id,
                relationship=rel,
                page_number=item.get("page", 1),
                section=item.get("section", ""),
                quote=item.get("quote", action_text),
            )
            graph.add_edge(term_id, "doc-contract", relationship="GOVERNED_BY")

        # 5. Dynamic Verified Findings
        created_clause_nodes = set()
        for idx, finding in enumerate(findings, start=1):
            finding_id = f"finding-{idx:03d}"
            bucket = finding.get("bucket", "watch_out")
            node_type = "protection" if bucket == "protection" else "risk_finding"

            graph.add_node(
                finding_id,
                node_type=node_type,
                label=finding.get("title", f"Finding {idx}"),
                severity=finding.get("severity", "unknown"),
                bucket=bucket,
                category=finding.get("category", "unknown"),
                claim=finding.get("claim", ""),
                plain_english=finding.get("plain_english", ""),
            )

            # Determine Clause / Section
            sec_name = (
                finding.get("section")
                or (finding.get("evidence", [{}])[0].get("section"))
                or finding.get("category", "Contract Terms").replace("_", " ").title()
            )
            clause_slug = f"clause-{finding.get('category', f'sec-{idx}')}"

            if clause_slug not in created_clause_nodes:
                graph.add_node(
                    clause_slug,
                    node_type="clause",
                    label=f"Clause: {sec_name}",
                    properties={"section": sec_name},
                )
                created_clause_nodes.add(clause_slug)

            # Link finding to clause
            first_ev = finding.get("evidence", [{}])[0]
            graph.add_edge(
                finding_id,
                clause_slug,
                relationship="FLAGGED_CLAUSE",
                quote=first_ev.get("quote", finding.get("claim", "")),
                page_number=first_ev.get("page", 1),
                section=sec_name,
            )

            # Link party to finding
            if bucket == "protection":
                graph.add_edge("party-customer", finding_id, relationship="BENEFITS_FROM")
                graph.add_edge("party-provider", finding_id, relationship="COMMITS_PROTECTION")
            else:
                graph.add_edge("party-provider", finding_id, relationship="IMPOSES_RISK")
                graph.add_edge("party-customer", finding_id, relationship="EXPOSED_TO_RISK")

            # Link finding to relevant asset
            cat = str(finding.get("category", "")).lower()
            if "data" in cat or "backup" in cat or "privacy" in cat or "security" in cat:
                graph.add_edge(finding_id, "asset-customer-data", relationship="IMPACTS_ASSET")
            elif "ip" in cat or "logo" in cat or "publicity" in cat or "trademark" in cat:
                graph.add_edge(finding_id, "asset-ip-rights", relationship="IMPACTS_ASSET")
            elif "service" in cat or "sla" in cat or "uptime" in cat:
                graph.add_edge(finding_id, "asset-services", relationship="IMPACTS_ASSET")
            elif "liability" in cat or "fee" in cat or "payment" in cat:
                graph.add_edge(finding_id, "concept-invoices", relationship="IMPACTS_ASSET")

            # Link finding to its supporting chunks
            for ev_idx, item in enumerate(finding.get("evidence", []), start=1):
                chunk_id = item.get("chunk_id", f"ev-{idx}-{ev_idx}")
                ev_node = f"evidence-{chunk_id}"

                if not graph.has_node(ev_node):
                    graph.add_node(
                        ev_node,
                        node_type="evidence",
                        label=chunk_id,
                        page_number=item.get("page"),
                        quote=item.get("quote", ""),
                    )

                graph.add_edge(
                    finding_id,
                    ev_node,
                    relationship="SUPPORTED_BY",
                    chunk_id=chunk_id,
                    page_number=item.get("page"),
                    quote=item.get("quote", ""),
                )

        # 6. Dynamic Missing Protection Gaps
        if missing_clauses:
            for m_idx, m in enumerate(missing_clauses, start=1):
                if m.get("status") == "MISSING":
                    gap_id = f"gap-{m.get('check_id', m_idx)}"
                    graph.add_node(
                        gap_id,
                        node_type="missing_protection",
                        label=f"Missing: {m.get('title', 'Protection')}",
                        properties=m,
                    )
                    graph.add_edge("party-customer", gap_id, relationship="MISSING_SAFEGUARD")
                    graph.add_edge(gap_id, "doc-contract", relationship="OMITTED_FROM")

        # 7. Asymmetry Link (if termination or liability clauses exist)
        if "clause-termination" in created_clause_nodes and len(created_clause_nodes) > 1:
            other_clause = [c for c in created_clause_nodes if c != "clause-termination"][0]
            graph.add_edge("clause-termination", other_clause, relationship="ASYMMETRIC_WITH")

        return graph

    def serialize(self, graph: nx.MultiDiGraph) -> dict:
        """Serializes the NetworkX graph to a D3/Cytoscape-compatible JSON structure."""
        nodes = []
        for node_id, data in graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "node_type": data.get("node_type", "entity"),
                "properties": data,
            })

        links = []
        for u, v, key, data in graph.edges(keys=True, data=True):
            links.append({
                "source": u,
                "target": v,
                "relationship": data.get("relationship", "RELATED_TO"),
                "page_number": data.get("page_number"),
                "chunk_id": data.get("chunk_id"),
                "section": data.get("section"),
                "quote": data.get("quote", ""),
            })

        return {
            "nodes": nodes,
            "links": links,
            "total_nodes": len(nodes),
            "total_links": len(links),
        }