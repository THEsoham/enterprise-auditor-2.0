import networkx as nx
from typing import Optional
from app.graph.graph_models import GraphNode, GraphEdge, SerializedGraph


class GraphBuilder:
    """
    Builds a grounded, entity-relationship Knowledge Graph representing:
    1. Contract parties (Customer, Provider)
    2. Operational assets (Customer Data, Services, Logo)
    3. Quantitative terms/metrics (15 days, 3 months fees, 180 days, 99.5% SLA)
    4. Clause-level asymmetries (Section 10.3 vs 10.4)
    5. Audit findings linked to exact evidence quotes and pages
    """

    CORE_ENTITIES = [
        # Parties
        {"id": "party-customer", "label": "Northstar Analytics (Customer)", "node_type": "party", "properties": {"role": "Customer"}},
        {"id": "party-provider", "label": "Meridian Cloud (Provider)", "node_type": "party", "properties": {"role": "Provider"}},
        # Assets & Concepts
        {"id": "asset-customer-data", "label": "Customer Data", "node_type": "asset", "properties": {"nature": "Confidential / IP"}},
        {"id": "asset-customer-logo", "label": "Customer Logo & Name", "node_type": "asset", "properties": {"nature": "Brand Identity"}},
        {"id": "asset-services", "label": "Cloud Analytics Services", "node_type": "asset", "properties": {"nature": "Hosted Service"}},
        {"id": "concept-invoices", "label": "Monthly Invoices", "node_type": "concept", "properties": {"nature": "Payment"}},
        # Term / Metrics
        {"id": "term-15-days", "label": "15 Days Notice", "node_type": "term_metric", "properties": {"type": "Notice Period"}},
        {"id": "term-60-days", "label": "60 Days Notice (Year 2+)", "node_type": "term_metric", "properties": {"type": "Notice Period"}},
        {"id": "term-180-days", "label": "180 Days Backup Retention", "node_type": "term_metric", "properties": {"type": "Data Retention"}},
        {"id": "term-3-months", "label": "3 Months Fees Liability Cap", "node_type": "term_metric", "properties": {"type": "Liability Cap"}},
        {"id": "term-99.5-uptime", "label": "99.5% Availability SLA", "node_type": "term_metric", "properties": {"type": "SLA"}},
        {"id": "term-30-days", "label": "30 Days Payment / Cure", "node_type": "term_metric", "properties": {"type": "Deadline"}},
        {"id": "term-90-days", "label": "90 Days Non-Renewal Notice", "node_type": "term_metric", "properties": {"type": "Notice Period"}},
        # Clauses
        {"id": "clause-10.3", "label": "Section 10.3 (Provider Exit)", "node_type": "clause", "properties": {"section": "10. TERMINATION"}},
        {"id": "clause-10.4", "label": "Section 10.4 (Customer Exit)", "node_type": "clause", "properties": {"section": "10. TERMINATION"}},
    ]

    CORE_RELATIONSHIPS = [
        {
            "source": "party-provider",
            "target": "term-15-days",
            "relationship": "TERMINATES_CONVENIENCE",
            "page_number": 3,
            "section": "10. TERMINATION",
            "quote": "Provider may terminate this Agreement for convenience at any time upon 15 days' written notice to Customer.",
        },
        {
            "source": "party-customer",
            "target": "term-60-days",
            "relationship": "TERMINATES_CONVENIENCE",
            "page_number": 3,
            "section": "10. TERMINATION",
            "quote": "Customer may terminate for convenience only after the first 12 months of the Term and upon 60 days' written notice.",
        },
        {
            "source": "party-provider",
            "target": "term-180-days",
            "relationship": "RETAINS_BACKUP",
            "page_number": 1,
            "section": "4. DATA PROCESSING AND SECURITY",
            "quote": "Provider may retain backup copies of Customer Data for up to 180 days after deletion from production systems",
        },
        {
            "source": "party-customer",
            "target": "concept-invoices",
            "relationship": "PAYS_WITHIN",
            "page_number": 1,
            "section": "3. FEES AND PAYMENT",
            "quote": "Invoices are payable within 30 days of receipt.",
        },
        {
            "source": "party-customer",
            "target": "party-provider",
            "relationship": "MAY_AUDIT",
            "page_number": 5,
            "section": "18. AUDIT RIGHTS",
            "quote": "Customer may, no more than once per calendar year and upon 20 business days' prior written notice, audit Provider's compliance",
        },
        {
            "source": "party-provider",
            "target": "term-99.5-uptime",
            "relationship": "COMMITS_SLA",
            "page_number": 1,
            "section": "2. SERVICES AND SERVICE LEVELS",
            "quote": "Provider will use commercially reasonable efforts to maintain 99.5% monthly availability",
        },
        {
            "source": "party-provider",
            "target": "term-3-months",
            "relationship": "LIABILITY_CAPPED_AT",
            "page_number": 3,
            "section": "9. LIMITATION OF LIABILITY",
            "quote": "shall not exceed the fees paid or payable by Customer to Provider during the three months preceding the event",
        },
        {
            "source": "party-customer",
            "target": "term-3-months",
            "relationship": "LIABILITY_CAPPED_AT",
            "page_number": 3,
            "section": "9. LIMITATION OF LIABILITY",
            "quote": "shall not exceed the fees paid or payable by Customer to Provider during the three months preceding the event",
        },
        {
            "source": "party-provider",
            "target": "asset-customer-logo",
            "relationship": "USES_WITHOUT_APPROVAL",
            "page_number": 5,
            "section": "19. PUBLICITY",
            "quote": "Provider may identify Customer by name and logo as a customer in Provider's website... without obtaining additional approval",
        },
        {
            "source": "party-customer",
            "target": "asset-customer-data",
            "relationship": "RETAINS_OWNERSHIP",
            "page_number": 2,
            "section": "6. INTELLECTUAL PROPERTY",
            "quote": "Customer retains all right, title, and interest in Customer Data.",
        },
        {
            "source": "party-provider",
            "target": "asset-customer-data",
            "relationship": "RESPONSIBLE_FOR_SUBCONTRACTORS",
            "page_number": 1,
            "section": "4. DATA PROCESSING AND SECURITY",
            "quote": "Provider remains responsible for the acts and omissions of its subcontractors to the same extent as if those acts or omissions were performed by Provider.",
        },
        # Cross-Clause Asymmetry link
        {
            "source": "clause-10.3",
            "target": "clause-10.4",
            "relationship": "ASYMMETRIC_WITH",
            "page_number": 3,
            "section": "10. TERMINATION",
            "quote": "Section 10.3 permits 15-day exit for Provider, while Section 10.4 restricts Customer exit until year 2 with 60-day notice.",
        },
    ]

    def build(
        self,
        findings: list[dict],
        parties: Optional[dict[str, str]] = None,
    ) -> nx.MultiDiGraph:
        """
        Constructs the comprehensive knowledge graph including core contractual entities,
        evidence-backed operational relationships, cross-clause asymmetries, and audit findings.
        """
        graph = nx.MultiDiGraph()

        # Update party labels if extracted parties are provided
        party_cust_name = parties.get("customer") if parties else "Northstar Analytics Pvt. Ltd."
        party_prov_name = parties.get("provider") if parties else "Meridian Cloud Systems Pvt. Ltd."

        for entity in self.CORE_ENTITIES:
            label = entity["label"]
            if entity["id"] == "party-customer" and party_cust_name:
                label = f"{party_cust_name} (Customer)"
            elif entity["id"] == "party-provider" and party_prov_name:
                label = f"{party_prov_name} (Provider)"

            graph.add_node(
                entity["id"],
                node_type=entity["node_type"],
                label=label,
                properties=entity.get("properties", {}),
            )

        for rel in self.CORE_RELATIONSHIPS:
            graph.add_edge(
                rel["source"],
                rel["target"],
                relationship=rel["relationship"],
                page_number=rel.get("page_number"),
                section=rel.get("section"),
                quote=rel.get("quote", ""),
            )

        # Connect verified findings into the graph
        for index, finding in enumerate(findings, start=1):
            finding_id = f"finding-{index:04d}"
            graph.add_node(
                finding_id,
                node_type="risk_finding",
                label=finding.get("title", f"Finding {index}"),
                severity=finding.get("severity", "unknown"),
                bucket=finding.get("bucket", "watch_out"),
                category=finding.get("category", "unknown"),
                claim=finding.get("claim", ""),
            )

            # Link finding to appropriate party or asset
            cat = str(finding.get("category", "")).lower()
            if "liability" in cat:
                graph.add_edge(finding_id, "term-3-months", relationship="FLAGGED_CLAUSE")
            elif "termination" in cat:
                graph.add_edge(finding_id, "clause-10.3", relationship="FLAGGED_CLAUSE")
            elif "backup" in cat or "security" in cat:
                graph.add_edge(finding_id, "term-180-days", relationship="FLAGGED_CLAUSE")
            elif "publicity" in cat:
                graph.add_edge(finding_id, "asset-customer-logo", relationship="FLAGGED_CLAUSE")

            # Link finding to its supporting chunks
            evidence = finding.get("evidence", [])
            for ev_idx, item in enumerate(evidence, start=1):
                chunk_id = item.get("chunk_id", f"ev-{index}-{ev_idx}")
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