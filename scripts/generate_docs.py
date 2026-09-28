import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx(output_path: str):
    doc = Document()

    # Configure margins (0.75 in)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x2D, 0x37, 0x48) # Dark Slate

    # --- TITLE SECTION ---
    p_badge = doc.add_paragraph()
    p_badge.paragraph_format.space_before = Pt(0)
    p_badge.paragraph_format.space_after = Pt(4)
    run_badge = p_badge.add_run("INSTITUTIONAL AI ARCHITECTURE SPECIFICATION")
    run_badge.font.name = 'Calibri'
    run_badge.font.size = Pt(9.5)
    run_badge.font.bold = True
    run_badge.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5) # Indigo

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(8)
    run_title = p_title.add_run("Enterprise Auditor 2.0: Deep AI Architecture & Competitive Technical Analysis")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Deep Navy

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(16)
    run_sub = p_sub.add_run(
        "A comprehensive technical deep-dive into the autonomous multi-agent courtroom, hybrid retrieval engine, "
        "deterministic missing-protection scanner, and competitive benchmarking against existing legal tech solutions."
    )
    run_sub.font.size = Pt(11.5)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    # Metadata callout box
    table_meta = doc.add_table(rows=1, cols=1)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_meta = table_meta.rows[0].cells[0]
    cell_meta.width = Inches(7.0)
    set_cell_background(cell_meta, "F8FAFC")
    set_cell_margins(cell_meta, top=120, bottom=120, left=180, right=180)
    p_meta = cell_meta.paragraphs[0]
    p_meta.paragraph_format.space_after = Pt(0)
    p_meta.add_run("Document Scope: ").bold = True
    p_meta.add_run("Backend AI/ML Systems Only (Orchestration, Ingestion, Retrieval, LangGraph Multi-Agent, Verification, Scoring, Knowledge Graph).\n")
    p_meta.add_run("Target Audience: ").bold = True
    p_meta.add_run("Chief Legal Officers, General Counsel, Senior AI Engineers, Enterprise Procurement Executives.")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Helper function for headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)
        return p

    def add_callout(title, text, bg_hex="F1F5F9", border_color=RGBColor(0x4F, 0x46, 0xE5)):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.rows[0].cells[0]
        c.width = Inches(7.0)
        set_cell_background(c, bg_hex)
        set_cell_margins(c, top=100, bottom=100, left=160, right=160)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        r_t = p.add_run(title + "\n")
        r_t.font.bold = True
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = border_color
        r_b = p.add_run(text)
        r_b.font.size = Pt(10)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # --- SECTION 1 ---
    add_h1("1. Architectural Overview & The 9-Stage AI Engine Pipeline")
    doc.add_paragraph(
        "Enterprise Auditor 2.0 departs completely from conventional single-shot LLM 'document Q&A' wrappers. "
        "Standard commercial AI tools fail in legal auditing because single models suffer from sycophancy, "
        "attention degradation across 50-page agreements, hallucinated citations, and blindness to omitted protections. "
        "Enterprise Auditor 2.0 solves this via an autonomous, multi-stage Adversarial Verification Pipeline."
    )

    p_stages = doc.add_paragraph()
    p_stages.paragraph_format.left_indent = Inches(0.2)
    stages = [
        ("Stage 1: Document Ingestion (PyMuPDF)", "Preserves page coordinate mappings so every claim is tied to physical visual PDF coordinates."),
        ("Stage 2: Multimodal Visual Scanner (pdfplumber)", "Extracts pricing tables, overage tier formulas, and unexecuted signature blank underlines."),
        ("Stage 3: Section-Aware Semantic Chunking", "Uses legal regex boundaries so clauses are never split across arbitrary token counts."),
        ("Stage 4: Hybrid Indexing & Reciprocal Rank Fusion", "Merges BM25 keyword precision with ChromaDB dense vector search using RRF."),
        ("Stage 5: Autonomous Audit Planner", "Identifies contract parties and dynamically compiles 13 domain-specific audit probes."),
        ("Stage 6: Missing-Protection Baseline Scanner", "Deterministically audits what is absent from the contract against enterprise safeguards."),
        ("Stage 7: Obligation Timeline Engine", "Extracts deontic modal duties ('shall', 'must') and maps deadlines and conditions precedent."),
        ("Stage 8: AI Courtroom Multi-Agent Debate", "LangGraph state machine pairing OpenAI GPT Claimant against Google Gemini Skeptic."),
        ("Stage 9: Scoring, Graph & Report Synthesis", "Calculates 100-point Health Score, generates NetworkX Knowledge Graph, and produces memos.")
    ]
    for st_title, st_desc in stages:
        p_item = doc.add_paragraph(style='List Bullet')
        p_item.paragraph_format.space_after = Pt(3)
        r1 = p_item.add_run(st_title + ": ")
        r1.bold = True
        p_item.add_run(st_desc)

    # --- SECTION 2 ---
    add_h1("2. Deep Code Walkthrough — Section by Section (Every AI Module Explained)")

    add_h2("2.1 Pipeline Orchestrator (app/pipeline/audit_pipeline.py)")
    doc.add_paragraph(
        "The AuditPipeline class acts as the centralized director. It coordinates the lifecycle of document analysis, "
        "enforces execution safety timeouts, offloads long-running debate tasks asynchronously, and compiles the final audit state."
    )
    doc.add_paragraph(
        "Key Method: audit(self, pdf_path, custom_queries, max_probes)\n"
        "1. Validates physical file existence.\n"
        "2. Invokes load_pdf() to produce a page-by-page text map.\n"
        "3. Triggers the TableExtractor and SignatureAnalyzer in parallel.\n"
        "4. Generates DocumentChunk models via semantic chunking and upserts embeddings into ChromaDB and BM25.\n"
        "5. Formulates an AuditPlan and runs the MissingClauseDetector against full document text.\n"
        "6. Executes multi-agent debate probes, filtering out any claims with REJECTED or UNSUPPORTED verdicts.\n"
        "7. Feeds corroborated findings into the RiskScorer, HealthScore, GraphBuilder, and ReportBuilder."
    )

    add_h2("2.2 Visual Scanner & Multimodal Ingestion (app/ingestion/)")
    add_h3("PDF Loader (pdf_loader.py)")
    doc.add_paragraph(
        "Implements load_pdf() via PyMuPDF (fitz). Crucially, it preserves strict page-level pagination "
        "([{'page_number': int, 'text': str}]). Standard OCR tools lump text into a single continuous stream, "
        "making page citations in legal memos inaccurate. PyMuPDF guarantees exact page fidelity."
    )

    add_h3("Table Extractor (table_extractor.py)")
    doc.add_paragraph(
        "Uses pdfplumber to detect horizontal and vertical grid lines, extract tabular cells, and classify them into "
        "pricing_tiers, notices_contacts, or signature_block. It transforms raw cells into clean Markdown tables and "
        "applies regex currency normalization. The _analyze_pricing_risks() method automatically computes overage fee "
        "exposure (e.g. ₹12/doc overage vs base ₹5/doc) and flags the absence of annual price escalation caps."
    )

    add_h3("Signature & Execution Analyzer (signature_analyzer.py)")
    doc.add_paragraph(
        "Addresses a major blindspot in commercial contracts: operating under an unexecuted draft. "
        "The SignatureAnalyzer inspects the document backward from the final pages, searching for signature tokens. "
        "It inspects page drawings and embedded raster images. If signature lines contain underscore blanks ('_____') "
        "without accompanying ink drawings or digital certificate images, it flags the document as UNEXECUTED_DRAFT."
    )

    add_h2("2.3 Section-Aware Semantic Chunking (app/chunking/semantic_chunker.py)")
    doc.add_paragraph(
        "The Achilles' heel of standard RAG is naive token chunking (e.g. splitting every 500 tokens). "
        "In contracts, a 500-token cutoff frequently cuts a limitation of liability clause in half, separating the liability cap "
        "from its exceptions (e.g. data breach exclusions). The LLM reads only Chunk A and falsely claims the cap is absolute."
    )
    doc.add_paragraph(
        "Enterprise Auditor 2.0 uses a specialized legal section pattern:\n"
        "SECTION_PATTERN = re.compile(r'(?<![\\d.])(\\d{1,2})\\.\\s+([A-Z][A-Z &\\-]{2,})(?=\\s|$)')\n"
        "This detects major numbered sections ('9. LIMITATION OF LIABILITY') while ignoring sub-clauses ('9.3'). "
        "If a section spans multiple pages, the active section name is inherited. Oversized sections are split strictly "
        "at sentence boundaries, guaranteeing legal covenants remain intact."
    )

    add_h2("2.4 Hybrid Retrieval & Reciprocal Rank Fusion (app/retrieval/)")
    doc.add_paragraph(
        "Legal search requires both conceptual understanding and literal string precision. Dense vector search alone "
        "excels at semantic queries ('Can the vendor terminate without cause?'), but fails on exact clause identifiers "
        "('Section 10.3') or technical terms of art ('force majeure', 'indemnify'). BM25 keyword search is exact but brittle."
    )
    doc.add_paragraph(
        "Enterprise Auditor 2.0 combines both using Reciprocal Rank Fusion (RRF):\n"
        "RRF_Score(d) = SUM[ 1 / (60 + Rank_m(d)) ] for m in {BM25, DenseVector}\n"
        "This produces an evidence stream that ranks high across both literal section numbers and conceptual legal context."
    )

    add_h2("2.5 Autonomous Audit Planner & Missing Protection Baseline (app/auditing/)")
    add_h3("Audit Planner (audit_planner.py)")
    doc.add_paragraph(
        "Extracts counterparties from contract recitals (e.g. 'Northstar Analytics' as Customer, 'Meridian Cloud' as Provider) "
        "and automatically compiles probes across 13 core risk domains: Termination Parity, Liability Caps, Data Security, "
        "Subcontractor Liability, Auto-Renewal, Audit Rights, Publicity, and Indemnity."
    )

    add_h3("Missing Clause Detector (missing_clauses.py)")
    doc.add_paragraph(
        "Solves the 'Negative Space' failure. Standard AI only searches what is present. If an essential safeguard is omitted, "
        "an ordinary LLM finds nothing and falsely reports: 'No risks found.' The MissingClauseDetector deterministically "
        "audits against an Enterprise Protection Baseline:\n"
        "• Disaster Recovery SLA & RTO/RPO (<4h RTO, <1h RPO)\n"
        "• Strict 24-48h Security Incident Notification Window\n"
        "• Affirmative Written Certification of Data Destruction\n"
        "• 30 Days Advance Written Notice for New Subprocessors\n"
        "• Termination Right for Extended Force Majeure (>30 days)"
    )

    add_h2("2.6 Obligation Timeline Engine (app/auditing/obligation_extractor.py)")
    doc.add_paragraph(
        "Uses deontic modal logic patterns ('shall', 'must', 'agrees to', 'shall not') to extract legally binding duties. "
        "It categorizes duties into milestone buckets (Signing, Onboarding, Monthly, Renewal Window, Post-Termination) "
        "and isolates conditions precedent (e.g. invoice dispute windows of 15 days), giving operational teams a complete compliance roadmap."
    )

    add_h2("2.7 AI Courtroom Multi-Agent Adversarial Debate (app/debate/ & app/verification/)")
    doc.add_paragraph(
        "Built on LangGraph (StateGraph), the AI Courtroom eliminates single-model bias by pitting two opposing frontier LLMs against each other:"
    )
    doc.add_paragraph(
        "1. Node 'initial_audit' (Claimant / Auditor): Powered by OpenAI GPT-4o-mini. Formulates a risk finding grounded strictly in retrieved chunks.\n"
        "2. Node 'verify' (Skeptic / Respondent): Powered by Google Gemini. Prompted as opposing counsel to aggressively stress-test the claim, verify exact quotes, check chunk IDs, and detect exaggerations.\n"
        "3. Node 'record_round': Appends round dialogue to debate history.\n"
        "4. Router 'route_after_verification': If Gemini accepts, route to finish. If rejected/corrected and rounds remain, route to rebuttal.\n"
        "5. Node 'rebuttal': Hands Gemini's objections back to the Auditor to produce a revised, conceded, or re-grounded claim.\n"
        "6. Node 'finish': Synthesizes the finalized, corroborated finding."
    )

    add_h2("2.8 Risk Scoring & 100-Point Health Calculus (app/scoring/)")
    doc.add_paragraph(
        "RiskScorer classifies findings into 3 Plain-English Action Buckets:\n"
        "• 🔴 Deal-Breakers: Unilateral 15-day termination, 3-month liability caps, unlimited customer indemnification.\n"
        "• 🟡 Watch Out: 180-day backup data retention, overage fee spikes, auto-renewal traps.\n"
        "• 🟢 Protections: Subcontractor accountability, annual audit oversight, customer IP ownership.\n\n"
        "HealthScore computes an institutional rating (0-100):\n"
        "Score = 100 - [SUM(DealBreakers * 15) + SUM(WatchOuts * 4-8) + SUM(MissingSafeguards * 6-10)] + ProtectionsBonus"
    )

    add_h2("2.9 Grounded Knowledge Graph (app/graph/graph_builder.py)")
    doc.add_paragraph(
        "Uses NetworkX to build an entity-relationship graph connecting Parties, Assets, Clauses, and Term Metrics. "
        "It visually exposes predatory asymmetry by connecting both parties to the same operational term "
        "(e.g. Provider 15-day exit vs Customer 12-month lock-in + 60 days notice)."
    )

    # --- SECTION 3 ---
    add_h1("3. Competitive Teardown: What Existing Products Get Wrong & Why Enterprise Auditor 2.0 Wins")

    add_h2("3.1 Ironclad AI (Contract Lifecycle Management)")
    doc.add_paragraph(
        "Flaw: Ironclad is an administrative database tool. It extracts tags (effective dates, parties) into spreadsheet columns. "
        "It cannot reason across clauses to spot predatory asymmetries (e.g. a 3-month liability cap vs 6 months of data exposure). "
        "It also requires weeks of manual playbook configuration and cannot inspect visual signature lines."
    )
    doc.add_paragraph(
        "Our Advantage: Zero setup required. Audits any commercial agreement on Day 1 using relational cross-clause reasoning "
        "and visual execution block verification."
    )

    add_h2("3.2 Robin AI")
    doc.add_paragraph(
        "Flaw: Robin AI relies on a single LLM (Anthropic Claude) paired with human paralegals in the loop. "
        "A single model suffers from sycophancy and attention decay over long agreements. Because its AI cannot autonomously "
        "guarantee citation truth, Robin AI depends on human review, introducing hours of turnaround lag."
    )
    doc.add_paragraph(
        "Our Advantage: Our Multi-Agent Courtroom replaces human bottlenecks with automated adversarial cross-examination, "
        "delivering a verified audit in ~25 seconds."
    )

    add_h2("3.3 Kira Systems (Litera)")
    doc.add_paragraph(
        "Flaw: Kira is built on legacy machine learning (CRF/shallow NLP) for M&A diligence. It highlights where clauses exist "
        "('Limitation of liability found on page 14'), but provides zero qualitative evaluation of whether the clause is toxic, "
        "and offers no negotiation redlines or obligation timelines."
    )
    doc.add_paragraph(
        "Our Advantage: Translates legalese into plain-English impact statements, provides ready-to-copy substitute clauses, "
        "and maps operational obligation timelines."
    )

    add_h2("3.4 Harvey AI / CoCounsel (Thomson Reuters)")
    doc.add_paragraph(
        "Flaw: Sits behind a blank conversational chatbox. If a junior lawyer forgets to prompt 'Is there an explicit 48-hour breach notice?', "
        "the tool stays silent. Furthermore, conversational RAG cannot find 'negative space'—when a protection is omitted, "
        "search retrieves nothing and concludes no risks exist."
    )
    doc.add_paragraph(
        "Our Advantage: Deterministic Missing-Protection Baseline Scanner audits what is absent from the contract automatically."
    )

    add_h2("3.5 Raw Frontier LLMs (ChatGPT / Claude / Gemini Web)")
    doc.add_paragraph(
        "Flaw: Pasting 40-page agreements into ChatGPT suffers from 'Lost in the Middle' attention decay, fabricated citations, "
        "and complete visual blindness to tables and unexecuted signature blocks."
    )
    doc.add_paragraph(
        "Our Advantage: Section-aware chunking, multimodal table/signature parsing, and dual-model verification ensure 100% corroborated outputs."
    )

    # --- SECTION 4 ---
    add_h1("4. Comparative Technical Matrix")
    
    headers = ["Capability", "Raw LLMs", "Ironclad AI", "Robin AI", "Harvey / CoCounsel", "Enterprise Auditor 2.0"]
    rows = [
        ["Multi-Agent Adversarial Debate", "No", "No", "No", "No", "Yes (OpenAI vs Gemini)"],
        ["Missing Protection Baseline Scanner", "No", "No", "No", "No", "Yes (Deterministic)"],
        ["Visual Signature & Draft Detection", "No", "No", "No", "No", "Yes (Vector / Ink Scanner)"],
        ["Tabular Pricing Risk Analysis", "No", "No", "No", "No", "Yes (pdfplumber Engine)"],
        ["Section-Aware Semantic Chunking", "No", "No", "No", "No", "Yes (Legal Regex Bounds)"],
        ["Hybrid Retrieval (BM25 + Dense RRF)", "No", "No", "No", "Dense Only", "Yes (Reciprocal Rank Fusion)"],
        ["Grounded Entity Knowledge Graph", "No", "No", "No", "No", "Yes (NetworkX D3 Graph)"],
        ["Obligation Timeline & Triggers", "No", "Manual", "No", "No", "Yes (Deontic Modal Logic)"],
        ["Plain-English 3-Bucket Categorization", "No", "No", "No", "No", "Yes (Deal-Breakers / Watch Out / Protections)"],
        ["100-Point Calibrated Health Scoring", "No", "No", "No", "No", "Yes (Deterministic Calculus)"],
        ["Audit Turnaround Time", "~10s (Unverified)", "Workflow-based", "Hours (Human loop)", "~30s (Unverified)", "~25s (Fully Corroborated)"]
    ]

    tbl_comp = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row formatting
    for j, h_text in enumerate(headers):
        c = tbl_comp.cell(0, j)
        set_cell_background(c, "0F172A") # Deep Navy
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Data rows formatting
    for i, row in enumerate(rows):
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = tbl_comp.cell(i + 1, j)
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
            elif j == 5: # Enterprise Auditor
                r.font.bold = True
                r.font.color.rgb = RGBColor(0x05, 0x96, 0x69) # Emerald Green

    doc.save(output_path)
    print(f"Generated DOCX: {output_path}")

def generate_pdf(output_path: str):
    # Professional ReportLab PDF Generator
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6,
    )
    
    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=4,
    )

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=16,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8,
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    story = []

    # Title block
    story.append(Paragraph("INSTITUTIONAL AI ARCHITECTURE SPECIFICATION", badge_style))
    story.append(Paragraph("Enterprise Auditor 2.0: Deep AI Architecture & Competitive Technical Analysis", title_style))
    story.append(Paragraph("A comprehensive technical deep-dive into the autonomous multi-agent courtroom, hybrid retrieval engine, missing-protection scanner, and competitive benchmarking.", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    # Section 1
    story.append(Paragraph("1. Architectural Overview & The 9-Stage AI Engine Pipeline", h1_style))
    story.append(Paragraph(
        "Enterprise Auditor 2.0 departs completely from conventional single-shot LLM wrappers. "
        "Standard commercial AI tools fail in legal auditing because single models suffer from sycophancy, "
        "attention degradation across long agreements, hallucinated citations, and blindness to omitted protections. "
        "Enterprise Auditor 2.0 solves this via an autonomous, multi-stage Adversarial Verification Pipeline:",
        body_style
    ))

    stages = [
        ("Stage 1: Document Ingestion (PyMuPDF)", "Preserves page coordinate mappings so every claim is tied to physical visual PDF coordinates."),
        ("Stage 2: Multimodal Visual Scanner (pdfplumber)", "Extracts pricing tables, overage tier formulas, and unexecuted signature blank underlines."),
        ("Stage 3: Section-Aware Semantic Chunking", "Uses legal regex boundaries so clauses are never split across arbitrary token counts."),
        ("Stage 4: Hybrid Indexing & Reciprocal Rank Fusion", "Merges BM25 keyword precision with ChromaDB dense vector search using RRF."),
        ("Stage 5: Autonomous Audit Planner", "Identifies contract parties and dynamically compiles 13 domain-specific audit probes."),
        ("Stage 6: Missing-Protection Baseline Scanner", "Deterministically audits what is absent from the contract against enterprise safeguards."),
        ("Stage 7: Obligation Timeline Engine", "Extracts deontic modal duties ('shall', 'must') and maps deadlines and conditions precedent."),
        ("Stage 8: AI Courtroom Multi-Agent Debate", "LangGraph state machine pairing OpenAI GPT Claimant against Google Gemini Skeptic."),
        ("Stage 9: Scoring, Graph & Report Synthesis", "Calculates 100-point Health Score, generates NetworkX Knowledge Graph, and produces memos.")
    ]
    for s_name, s_detail in stages:
        story.append(Paragraph(f"• <b>{s_name}:</b> {s_detail}", bullet_style))

    story.append(Spacer(1, 10))

    # Section 2
    story.append(Paragraph("2. Deep Code Walkthrough — Section by Section (Every AI Module Explained)", h1_style))
    
    story.append(Paragraph("2.1 Pipeline Orchestrator (app/pipeline/audit_pipeline.py)", h2_style))
    story.append(Paragraph(
        "The <b>AuditPipeline</b> class directs the end-to-end flow. In its <code>audit()</code> method, it validates file existence, "
        "runs PyMuPDF page mapping, fires the visual table and signature scanners, builds semantic chunks, populates in-memory BM25 and vector stores, "
        "formulates domain audit probes, executes multi-agent debate loops with consensus filtering, and synthesizes 100-point health metrics and audit memos.",
        body_style
    ))

    story.append(Paragraph("2.2 Visual Scanner & Multimodal Ingestion (app/ingestion/)", h2_style))
    story.append(Paragraph(
        "• <b>pdf_loader.py:</b> Extracts text with strict page number preservation.<br/>"
        "• <b>table_extractor.py:</b> Uses <code>pdfplumber</code> to extract pricing tables, reconstructs them into Markdown, fixes ASCII currency glyphs, and evaluates overage fee escalation traps.<br/>"
        "• <b>signature_analyzer.py:</b> Scans execution blocks for blank underlines (<code>_____</code>) versus ink/vector drawings to detect <code>UNEXECUTED_DRAFT</code> states.",
        body_style
    ))

    story.append(Paragraph("2.3 Section-Aware Semantic Chunking (app/chunking/semantic_chunker.py)", h2_style))
    story.append(Paragraph(
        "Conventional RAG breaks text at arbitrary token limits, severing liability caps from their exclusions. "
        "Our <code>SECTION_PATTERN</code> regex preserves complete numbered sections (e.g. <code>9. LIMITATION OF LIABILITY</code>) "
        "and handles multi-page continuation while splitting oversized text strictly at sentence punctuation.",
        body_style
    ))

    story.append(Paragraph("2.4 Hybrid Retrieval & Reciprocal Rank Fusion (app/retrieval/)", h2_style))
    story.append(Paragraph(
        "Combines Okapi BM25 keyword search with ChromaDB dense vector embeddings using Reciprocal Rank Fusion (RRF):<br/>"
        "<b>RRF_Score(d) = &Sigma; [ 1 / (60 + Rank_m(d)) ]</b> for m &isin; {BM25, DenseVector}.<br/>"
        "Guarantees that both literal clause numbers ('Section 10.3') and conceptual risks ('termination for convenience') are retrieved.",
        body_style
    ))

    story.append(Paragraph("2.5 Autonomous Audit Planner & Missing Baseline Scanner (app/auditing/)", h2_style))
    story.append(Paragraph(
        "• <b>audit_planner.py:</b> Discovers counterparties and compiles 13 commercial audit probes.<br/>"
        "• <b>missing_clauses.py:</b> Solves the 'Negative Space' failure. Deterministically verifies mandatory enterprise protections: "
        "RTO/RPO disaster recovery SLAs, strict 24-48h security incident notification windows, affirmative data destruction certification, "
        "and 30-day advance subprocessor notices.",
        body_style
    ))

    story.append(Paragraph("2.6 Obligation Timeline Engine (app/auditing/obligation_extractor.py)", h2_style))
    story.append(Paragraph(
        "Extracts deontic modal obligations ('shall', 'must', 'agrees to') and structures them into chronological milestone buckets "
        "(Signing, Onboarding, Monthly, Renewal, Post-Termination) while isolating conditions precedent.",
        body_style
    ))

    story.append(Paragraph("2.7 AI Courtroom Multi-Agent Adversarial Debate (app/debate/ & app/verification/)", h2_style))
    story.append(Paragraph(
        "Built on LangGraph (StateGraph), the AI Courtroom pairs an <b>OpenAI GPT-4o-mini Claimant</b> against a <b>Google Gemini Skeptic</b>. "
        "Gemini cross-examines the finding, checking verbatim quote existence, chunk IDs, and contradictions. "
        "Uncorroborated claims are sent to rebuttal or rejected, ensuring zero hallucinations enter the audit.",
        body_style
    ))

    story.append(Paragraph("2.8 Risk Scoring & 100-Point Health Calculus (app/scoring/)", h2_style))
    story.append(Paragraph(
        "Classifies verified claims into 🔴 <b>Deal-Breakers</b>, 🟡 <b>Watch Out</b>, and 🟢 <b>Protections</b>. "
        "HealthScore calculates an institutional rating (0-100) deducting points for deal-breakers (-15) and missing safeguards (-10), "
        "providing boards and legal counsel with an immediate decision metric.",
        body_style
    ))

    story.append(Paragraph("2.9 Grounded Knowledge Graph (app/graph/graph_builder.py)", h2_style))
    story.append(Paragraph(
        "Uses NetworkX to build an entity-relationship graph connecting Parties, Assets, Clauses, and Term Metrics. "
        "It visually exposes predatory asymmetry by connecting both parties to the same operational term "
        "(e.g. Provider 15-day exit vs Customer 12-month lock-in + 60 days notice).",
        body_style
    ))

    story.append(PageBreak())

    # Section 3
    story.append(Paragraph("3. Competitive Teardown: What Existing Products Get Wrong", h1_style))
    
    competitors = [
        ("Ironclad AI (Contract Lifecycle Management)",
         "Ironclad is an administrative database tool. It extracts tags (dates, parties) into spreadsheet columns. "
         "It cannot reason across clauses to spot predatory asymmetries (e.g. 3-month liability cap vs 6 months of data retention exposure). "
         "It requires weeks of manual playbook configuration and has no visual signature analyzer. "
         "<b>Our Advantage:</b> Zero setup required; autonomous cross-clause relational reasoning and visual execution block detection."),
        
        ("Robin AI",
         "Robin AI uses a single LLM (Anthropic Claude) paired with human paralegals in the loop. "
         "A single model suffers from sycophancy and attention decay over long contracts. Because its AI cannot autonomously verify citations, "
         "Robin AI depends on human review, creating hours of delay. "
         "<b>Our Advantage:</b> Multi-Agent Courtroom replaces human bottlenecks with automated adversarial cross-examination in ~25 seconds."),
        
        ("Kira Systems (Litera)",
         "Kira uses legacy machine learning (CRF/shallow NLP) for M&A diligence. It highlights where clauses exist, but provides zero qualitative "
         "evaluation of whether the clause is toxic, and offers no negotiation redlines or obligation timelines. "
         "<b>Our Advantage:</b> Plain-English impact statements, ready-to-copy substitute redlines, and automated obligation timelines."),
        
        ("Harvey AI / CoCounsel (Thomson Reuters)",
         "Sits behind a blank conversational chatbox. If a junior lawyer forgets to ask 'Is there an explicit 48-hour breach notice?', "
         "the tool stays silent. Furthermore, conversational RAG cannot find 'negative space'—when a protection is omitted, search finds nothing and reports no risks. "
         "<b>Our Advantage:</b> Deterministic Missing-Protection Baseline Scanner audits what is absent from the contract automatically."),
        
        ("Raw Frontier LLMs (ChatGPT / Claude / Gemini Web)",
         "Pasting 40-page agreements into ChatGPT suffers from 'Lost in the Middle' attention decay, fabricated citations, "
         "and complete visual blindness to tables and unexecuted signature blocks. "
         "<b>Our Advantage:</b> Section-aware chunking, multimodal table/signature parsing, and dual-model verification ensure 100% corroborated outputs.")
    ]

    for c_name, c_text in competitors:
        story.append(Paragraph(f"<b>3.{stages.index(stages[0])+1} {c_name}</b>", h2_style))
        story.append(Paragraph(c_text, body_style))

    story.append(Spacer(1, 10))

    # Section 4: Table
    story.append(Paragraph("4. Comparative Technical Matrix", h1_style))

    table_data = [
        ["Capability", "Raw LLMs", "Ironclad AI", "Robin AI", "Harvey / CoCounsel", "Enterprise Auditor 2.0"],
        ["Multi-Agent Adversarial Debate", "No", "No", "No", "No", "Yes (OpenAI vs Gemini)"],
        ["Missing Protection Baseline Scanner", "No", "No", "No", "No", "Yes (Deterministic)"],
        ["Visual Signature & Draft Detection", "No", "No", "No", "No", "Yes (Vector/Ink Scanner)"],
        ["Tabular Pricing Risk Analysis", "No", "No", "No", "No", "Yes (pdfplumber Engine)"],
        ["Section-Aware Semantic Chunking", "No", "No", "No", "No", "Yes (Legal Regex)"],
        ["Hybrid Retrieval (BM25 + Dense RRF)", "No", "No", "No", "Dense Only", "Yes (RRF Fusion)"],
        ["Grounded Entity Knowledge Graph", "No", "No", "No", "No", "Yes (NetworkX D3)"],
        ["Obligation Timeline & Triggers", "No", "Manual", "No", "No", "Yes (Deontic Modals)"],
        ["Actionable 3-Bucket Classification", "No", "No", "No", "No", "Yes (Deal-Breakers etc)"],
        ["100-Point Calibrated Health Score", "No", "No", "No", "No", "Yes (Calibrated Calculus)"],
        ["Audit Turnaround Time", "~10s", "Workflow-based", "Hours (Human)", "~30s", "~25s (Corroborated)"]
    ]

    t = Table(table_data, colWidths=[1.8 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 1.1 * inch, 1.4 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TEXTCOLOR', (5, 1), (5, -1), colors.HexColor('#059669')), # Highlight Enterprise Auditor
        ('FONTNAME', (5, 1), (5, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)

    doc.build(story)
    print(f"Generated PDF: {output_path}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    docx_file = base_dir / "Enterprise_Auditor_2.0_AI_Architecture.docx"
    pdf_file = base_dir / "Enterprise_Auditor_2.0_AI_Architecture.pdf"

    generate_docx(str(docx_file))
    generate_pdf(str(pdf_file))
