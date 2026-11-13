import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles to prevent charmap UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.ingestion.docx_reader import docx_to_text, extract_docx_tables
from app.pipeline.audit_pipeline import AuditPipeline
from app.debate.debate_graph import DebateEngine
from app.scoring.risk_scorer import RiskScorer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"

load_dotenv(PROJECT_ROOT / ".env")

# Every audit resets and refills the shared vector index, so audits must not overlap
AUDIT_LOCK = asyncio.Lock()

# The contract currently loaded in the retrieval index; debates search this document
indexed_document: Optional[Path] = None

app = FastAPI(
    title="Enterprise Auditor 2.0 API",
    description="Autonomous Contract Auditing, AI Courtroom, and Visual Scanner",
    version="2.0.0",
)

# Enable CORS
# CORS = Cross-Origin Resource Sharing.
app.add_middleware(
    CORSMiddleware,
    # The frontend is served from this same app, so no other site needs access by default
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    query: str
    max_rounds: Optional[int] = None


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "system": "Enterprise Auditor 2.0",
        "models": {
            "auditor": f"OpenAI {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}",
            "verifier": (
                f"Gemini {os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')} "
                f"(fallbacks: {os.getenv('GEMINI_FALLBACK_MODELS', 'gemini-3.6-flash')}, "
                f"then OpenAI {os.getenv('OPENAI_VERIFIER_MODEL', 'gpt-4o')})"
                if os.getenv("GEMINI_API_KEY") and os.getenv("USE_GEMINI", "true").lower() == "true"
                else f"OpenAI {os.getenv('OPENAI_VERIFIER_MODEL', 'gpt-4o')}"
            ),
        }
    }


def _safe_document_path(filename: str) -> Path:
    """Resolve a filename inside data/documents, rejecting path traversal."""
    path = (DOCUMENTS_DIR / Path(filename).name).resolve()
    if path.parent != DOCUMENTS_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename.")
    return path


def _decode_text(content: bytes) -> str:
    """
    Decode an uploaded text file without silently dropping characters.
    Tries a byte-order mark, then UTF-8, then Windows-1252 (what Notepad and Word
    save as when a file is not UTF-8). Bytes that fit none of these become U+FFFD.
    """
    if content.startswith((b"\xff\xfe", b"\xfe\xff")):
        return content.decode("utf-16")
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("cp1252", errors="replace")


def _text_to_pdf(text: str, pdf_path: Path) -> None:
    """
    Render plain text into a paginated PDF. Long lines wrap and pages break on their own.
    PyMuPDF's Story layout switches to a built-in fallback font for any character the
    main font lacks, so symbols (₹, curly quotes) and other scripts (Hindi, Chinese,
    Arabic) are drawn instead of being replaced by dots.
    """
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz
    import html

    body = html.escape(text or " ")
    story = fitz.Story(
        html=f"<p style='font-family: sans-serif; font-size: 10pt; white-space: pre-wrap;'>{body}</p>"
    )
    page_rect = fitz.paper_rect("a4")
    text_area = page_rect + (50, 50, -50, -50)

    writer = fitz.DocumentWriter(str(pdf_path))
    more = True
    while more:
        device = writer.begin_page(page_rect)
        more, _ = story.place(text_area)
        story.draw(device)
        writer.end_page()
    writer.close()


def _pdf_has_text(content: bytes) -> bool:
    """False for corrupt PDFs and for image-only PDFs such as scans."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    try:
        with fitz.open(stream=content, filetype="pdf") as doc:
            return any(page.get_text("text").strip() for page in doc)
    except Exception:
        return False


def _saved_report(pdf_path: Path) -> Optional[dict]:
    """A previous audit of this exact file, unless it found nothing (e.g. an API outage)."""
    report_path = REPORTS_DIR / f"{pdf_path.stem}_audit.json"
    if not report_path.exists():
        return None
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    return report if report.get("findings") else None


async def _run_pipeline(
    pdf_path: Path,
    max_probes: int,
    display_name: Optional[str] = None,
    source_format: Optional[str] = None,
    tables: Optional[list] = None,
) -> dict:
    global indexed_document
    async with AUDIT_LOCK:
        pipeline = AuditPipeline(max_debate_rounds=int(os.getenv("MAX_DEBATE_ROUNDS", "2")))
        result = await asyncio.to_thread(
            pipeline.audit,
            pdf_path=pdf_path,
            max_probes=max_probes,
            display_name=display_name,
            source_format=source_format,
            tables=tables,
        )
        indexed_document = pdf_path
        return result


async def _ensure_indexed(pdf_path: Path) -> None:
    """Load a contract into the retrieval index without re-running the audit."""
    global indexed_document
    async with AUDIT_LOCK:
        if indexed_document != pdf_path:
            await asyncio.to_thread(AuditPipeline(max_debate_rounds=1).index_document, pdf_path)
            indexed_document = pdf_path


@app.get("/api/sample/demo")
async def get_sample_demo_report():
    """Load the pre-computed sample contract audit on demand for demonstration."""
    pdf_path = DOCUMENTS_DIR / "sample_contract.pdf"
    sample_files = list(REPORTS_DIR.glob("sample_contract*_audit.json"))
    if sample_files:
        sample_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        with open(sample_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)

        # Debates on the demo page must search the sample contract, not the last upload
        if pdf_path.exists():
            await _ensure_indexed(pdf_path)
        return {"report": data}

    if pdf_path.exists():
        res = await _run_pipeline(pdf_path, max_probes=5)
        return {"report": res["report"]}

    raise HTTPException(status_code=404, detail="Sample contract not found.")


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new contract PDF/text document and run the autonomous audit pipeline."""
    allowed_exts = {".pdf", ".txt", ".docx", ".md"}
    original_name = Path(file.filename or "").name
    ext = Path(original_name).suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: PDF, TXT, DOCX, MD."
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    stem = Path(original_name).stem
    content = await file.read()

    # Identical uploads share one stored file, so their audit can be reused
    content_id = hashlib.sha256(content).hexdigest()[:12]

    if ext == ".pdf":
        if not _pdf_has_text(content):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{original_name} contains no readable text. Scanned PDFs are not supported yet; "
                    "please upload a PDF with selectable text."
                ),
            )

        dest_path = _safe_document_path(original_name)
        if dest_path.exists() and dest_path.read_bytes() != content:
            dest_path = _safe_document_path(f"{stem}_{content_id}{ext}")
        if not dest_path.exists():
            dest_path.write_bytes(content)
    else:
        # The pipeline reads PDFs, so convert text/markdown/docx first
        try:
            text_str = docx_to_text(content) if ext == ".docx" else _decode_text(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read {original_name}: {e}")

        if not text_str.strip():
            raise HTTPException(status_code=400, detail=f"{original_name} contains no readable text.")

        dest_path = _safe_document_path(f"{stem}_{content_id}_converted.pdf")
        if not dest_path.exists():
            _text_to_pdf(text_str, dest_path)

    saved_report = _saved_report(dest_path)
    if saved_report:
        # Debates must search this contract, even though the audit is not re-run
        await _ensure_indexed(dest_path)
        return {
            "status": "success",
            "filename": original_name,
            "report": saved_report,
            "message": f"Loaded the saved audit of {original_name}",
        }

    # DOCX tables are read straight from the file, since conversion flattens them
    docx_tables = None
    if ext == ".docx":
        try:
            docx_tables = [t.model_dump() for t in extract_docx_tables(content)]
        except Exception:
            docx_tables = None

    try:
        result = await _run_pipeline(
            dest_path,
            max_probes=int(os.getenv("UPLOAD_MAX_PROBES", "12")),
            display_name=original_name,
            # Converted files have no real pages or signature images to analyse
            source_format=None if ext == ".pdf" else ext,
            tables=docx_tables,
        )
        return {
            "status": "success",
            "filename": original_name,
            "report": result["report"],
            "message": f"Successfully audited {original_name}",
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Audit failed for {original_name}: {str(e)}")


@app.post("/api/debate")
async def run_courtroom_debate(req: DebateRequest):
    """
    Run an interactive multi-turn AI Courtroom debate for a custom query.
    OpenAI Auditor ↔ Gemini Skeptic ↔ Auditor Rebuttal.
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Debates search the index of the last audited contract, so wait for any running audit
    async with AUDIT_LOCK:
        max_rounds = req.max_rounds or int(os.getenv("MAX_DEBATE_ROUNDS", "2"))
        engine = DebateEngine(max_rounds=max(1, min(max_rounds, 4)))
        result = await asyncio.to_thread(engine.run, query=query)

    finding = result.get("finding") or {}
    verification = result.get("verification") or {}
    history = result.get("history") or []
    verdict = str(verification.get("verdict", "UNSUPPORTED")).upper()

    risk_score = RiskScorer().score(finding=finding, verification=verification) if finding else {}

    return {
        "query": query,
        "verdict": verdict,
        "status": result.get("final_status", verdict),
        "verifier_model": verification.get("verifier_model", ""),
        "finding": finding,
        "verification": verification,
        "history": history,
        "risk_score": risk_score,
        "plain_english": finding.get("plain_english", ""),
        "why_flagged": finding.get("why_flagged", verification.get("reasoning", "")),
        "suggested_negotiation": finding.get("suggested_negotiation", ""),
        "clause_balance": finding.get("clause_balance", {"is_asymmetric": False}),
        "evidence": finding.get("evidence", []),
    }


@app.get("/api/download/memo")
async def download_audit_memo(document: str):
    """Download the executive Markdown audit memo for the named contract."""
    memo_path = REPORTS_DIR / f"{Path(Path(document).name).stem}_audit_memo.md"
    if not memo_path.exists():
        raise HTTPException(status_code=404, detail="No audit memo found for this contract.")

    return FileResponse(
        path=memo_path,
        filename=memo_path.name,
        media_type="text/markdown",
    )


# Mount frontend static files
frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
