from pathlib import Path
from typing import Optional

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.table_extractor import TableExtractor
from app.ingestion.signature_analyzer import SignatureAnalyzer
from app.chunking.semantic_chunker import chunk_pages
from app.retrieval.retriever import Retriever
from app.auditing.audit_planner import AuditPlanner, AuditProbe
from app.auditing.missing_clauses import MissingClauseDetector
from app.auditing.obligation_extractor import ObligationExtractor
from app.debate.debate_graph import DebateEngine
from app.scoring.risk_scorer import RiskScorer
from app.scoring.health_score import HealthScore
from app.graph.graph_builder import GraphBuilder
from app.reports.report_builder import ReportBuilder
from app.reports.json_exporter import JsonExporter
from app.reports.markdown_exporter import MarkdownExporter


class AuditPipeline:
    """
    Enterprise Auditor 2.0 Unified End-to-End Engine.
    Executes autonomous contract ingestion, table extraction, visual signature analysis,
    hybrid retrieval indexing, audit planning, multi-agent courtroom debate,
    risk scoring across 3 plain-English buckets, 100-point health scoring,
    grounded knowledge graph synthesis, and executive report generation.
    """

    def __init__(self, max_debate_rounds: int = 3):
        self.table_extractor = TableExtractor()
        self.signature_analyzer = SignatureAnalyzer()
        self.retriever = Retriever()
        self.audit_planner = AuditPlanner()
        self.missing_clause_detector = MissingClauseDetector()
        self.obligation_extractor = ObligationExtractor()
        self.debate = DebateEngine(max_rounds=max_debate_rounds)
        self.risk_scorer = RiskScorer()
        self.health = HealthScore()
        self.graph_builder = GraphBuilder()
        self.report_builder = ReportBuilder()
        self.json_exporter = JsonExporter()
        self.markdown_exporter = MarkdownExporter()

    def audit(
        self,
        pdf_path: str | Path,
        custom_queries: Optional[list[str]] = None,
        max_probes: Optional[int] = None,
    ) -> dict:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        document_name = pdf_path.name
        print(f"\n=======================================================")
        print(f"🛡️  ENTERPRISE AUDITOR 2.0: AUDITING {document_name}")
        print(f"=======================================================\n")

        # 1. Ingestion
        print("📄 [1/9] Ingesting PDF and mapping pages...")
        pages = load_pdf(pdf_path)
        full_text = "\n".join(p["text"] for p in pages)

        # 2. Visual Scanner: Tables & Signatures
        print("🔎 [2/9] Running Visual Scanner (tables & signature blocks)...")
        extracted_tables = self.table_extractor.extract_tables(pdf_path)
        tables_data = [t.model_dump() for t in extracted_tables]

        signature_status = self.signature_analyzer.analyze(pdf_path)
        signature_data = signature_status.model_dump()

        # 3. Chunking & Indexing
        print("🧩 [3/9] Creating section-aware semantic chunks...")
        doc_chunks = chunk_pages(pages)
        raw_chunks = [c.model_dump() for c in doc_chunks]

        print("🔍 [4/9] Populating Hybrid Retrieval (BM25 + Vector embeddings)...")
        # Upsert chunks into Chroma using fast batched embeddings
        chunk_texts = [c["text"] for c in raw_chunks]
        embeddings = self.retriever.embedding_service.embed_batch(chunk_texts)
        self.retriever.vector_store.add_chunks(chunks=raw_chunks, embeddings=embeddings)
        self.retriever.index_chunks(raw_chunks)

        # 4. Document Planning & Baseline Checks
        print("📋 [5/9] Formulating Audit Plan & Party Extraction...")
        plan = self.audit_planner.create_plan(raw_chunks, document_title=document_name)
        parties = plan.parties

        print("⚠️ [6/9] Running Missing-Protection Baseline Scanner...")
        missing_clauses = self.missing_clause_detector.detect(full_text)

        print("📅 [7/9] Extracting Obligations & Constructing Timeline Map...")
        obligations_summary = self.obligation_extractor.extract(raw_chunks)
        obligations_data = obligations_summary.model_dump()

        # 5. Multi-Agent Courtroom Debate
        print("⚖️ [8/9] Running AI Courtroom Multi-Agent Debate...")
        probes_to_run = plan.probes
        if custom_queries:
            probes_to_run = [
                AuditProbe(
                    probe_id=f"custom-{i+1}",
                    category="custom",
                    target_area="User Query",
                    query=q,
                    priority="high"
                )
                for i, q in enumerate(custom_queries)
            ]
        elif max_probes:
            probes_to_run = probes_to_run[:max_probes]

        findings = []
        risk_scores = []
        debate_histories = []

        for probe in probes_to_run:
            query_text = probe.query if isinstance(probe, AuditProbe) else probe.get("query", "")
            target_area = probe.target_area if isinstance(probe, AuditProbe) else probe.get("target_area", "")
            print(f"  → Debating probe: {target_area or query_text[:50]}...")

            try:
                result = self.debate.run(query=query_text)
                finding = result.get("finding")
                verification = result.get("verification")

                if not finding or not verification:
                    continue

                verdict = str(verification.get("verdict", "")).upper()
                if verdict in {"REJECTED", "UNSUPPORTED"}:
                    continue

                # Score finding and classify into Deal-Breaker / Watch Out / Protection
                risk_score = self.risk_scorer.score(
                    finding=finding,
                    verification=verification,
                )

                findings.append(finding)
                risk_scores.append(risk_score)
                debate_histories.append(result.get("history", []))
            except Exception as probe_err:
                print(f"  ⚠️ Probe '{target_area}' skipped: {probe_err}")
                continue

        # 6. Scoring, Graph & Reports
        print("📊 [9/9] Synthesizing Health Score, Knowledge Graph, and Audit Memo...")
        health_score = self.health.calculate(
            findings=findings,
            risk_scores=risk_scores,
            missing_clauses=missing_clauses,
        )

        nx_graph = self.graph_builder.build(
            findings=findings,
            parties=parties,
        )
        serialized_graph = self.graph_builder.serialize(nx_graph)

        report = self.report_builder.build(
            document_name=document_name,
            findings=findings,
            risk_scores=risk_scores,
            health_score=health_score,
            debate_histories=debate_histories,
            missing_clauses=missing_clauses,
            obligations=obligations_data,
            tables=tables_data,
            signature_status=signature_data,
            graph_data=serialized_graph,
            parties=parties,
        )

        # Export report artifacts
        json_path = self.json_exporter.export(report)
        md_path = self.markdown_exporter.export(report)

        print("\n" + "=" * 55)
        print(f"✅ AUDIT COMPLETE: {health_score.get('headline')}")
        print(f"📄 JSON Report: {json_path}")
        print(f"📝 Audit Memo:  {md_path}")
        print("=" * 55 + "\n")

        return {
            "report": report,
            "health": health_score,
            "findings": findings,
            "risk_scores": risk_scores,
            "missing_clauses": missing_clauses,
            "obligations": obligations_data,
            "tables": tables_data,
            "signature_status": signature_data,
            "graph": serialized_graph,
            "json_path": str(json_path),
            "markdown_path": str(md_path),
        }