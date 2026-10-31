import asyncio
import json
import os
import sys
import textwrap
import time
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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    query: str
    max_rounds: Optional[int] = None


class AuditRequest(BaseModel):
    filename: Optional[str] = "sample_contract.pdf"
    max_probes: Optional[int] = 7


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "system": "Enterprise Auditor 2.0",
        "models": {
            "auditor": f"OpenAI {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}",
            "verifier": (
                f"Gemini {os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')} "
                f"(fallbacks: {os.getenv('GEMINI_FALLBACK_MODELS', 'gemini-3.6-flash')}, then OpenAI)"
                if os.getenv("GEMINI_API_KEY") and os.getenv("USE_GEMINI", "true").lower() == "true"
                else f"OpenAI {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}"
            ),
        }
    }


def _safe_document_path(filename: str) -> Path:
    """Resolve a filename inside data/documents, rejecting path traversal."""
    path = (DOCUMENTS_DIR / Path(filename).name).resolve()
    if path.parent != DOCUMENTS_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename.")
    return path


def _docx_to_text(content: bytes) -> str:
    import io
    import zipfile
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(io.BytesIO(content)) as z:
        tree = ET.fromstring(z.read("word/document.xml"))

    # One line per paragraph (<w:p>), joining its text runs (<w:t>)
    paragraphs = []
    for node in tree.iter():
        if node.tag.endswith("}p"):
            text = "".join(t.text or "" for t in node.iter() if t.tag.endswith("}t"))
            if text.strip():
                paragraphs.append(text)
    return "\n".join(paragraphs)


def _text_to_pdf(text: str, pdf_path: Path) -> None:
    """Render plain text into a paginated PDF, wrapping long lines instead of truncating."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    lines = []
    for raw_line in text.splitlines() or [""]:
        lines.extend(textwrap.wrap(raw_line, width=95) or [""])

    lines_per_page = 60
    doc = fitz.open()
    for i in range(0, max(len(lines), 1), lines_per_page):
        page = doc.new_page()
        page.insert_text((50, 50), "\n".join(lines[i : i + lines_per_page]), fontsize=10)
    doc.save(pdf_path)
    doc.close()


async def _run_pipeline(pdf_path: Path, max_probes: int) -> dict:
    global indexed_document
    async with AUDIT_LOCK:
        pipeline = AuditPipeline(max_debate_rounds=int(os.getenv("MAX_DEBATE_ROUNDS", "2")))
        result = await asyncio.to_thread(pipeline.audit, pdf_path=pdf_path, max_probes=max_probes)
        indexed_document = pdf_path
        return result


async def _ensure_indexed(pdf_path: Path) -> None:
    """Load a contract into the retrieval index without re-running the audit."""
    global indexed_document
    async with AUDIT_LOCK:
        if indexed_document != pdf_path:
            await asyncio.to_thread(AuditPipeline(max_debate_rounds=1).index_document, pdf_path)
            indexed_document = pdf_path


@app.get("/api/report/latest")
async def get_latest_report():
    """Retrieve the most recently generated audit report JSON."""
    report_files = sorted(REPORTS_DIR.glob("*_audit.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if report_files:
        with open(report_files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    raise HTTPException(status_code=404, detail="No audit report found.")


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

    if ext == ".pdf":
        dest_path = _safe_document_path(original_name)
        if dest_path.exists():
            dest_path = _safe_document_path(f"{stem}_{int(time.time())}{ext}")
        dest_path.write_bytes(content)
    else:
        # The pipeline reads PDFs, so convert text/markdown/docx first
        try:
            text_str = _docx_to_text(content) if ext == ".docx" else content.decode("utf-8", errors="ignore")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read {original_name}: {e}")

        if not text_str.strip():
            raise HTTPException(status_code=400, detail=f"{original_name} contains no readable text.")

        dest_path = _safe_document_path(f"{stem}_{int(time.time())}_converted.pdf")
        _text_to_pdf(text_str, dest_path)

    try:
        result = await _run_pipeline(dest_path, max_probes=4)
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


@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    """Execute autonomous audit pipeline on the specified contract PDF."""
    pdf_path = _safe_document_path(req.filename or "")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Contract not found: {req.filename}")

    result = await _run_pipeline(pdf_path, max_probes=req.max_probes)
    return result["report"]


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
async def download_audit_memo():
    """Download the executive Markdown audit memo for the latest audited contract."""
    memo_files = list(REPORTS_DIR.glob("*_audit_memo.md"))
    if not memo_files:
        raise HTTPException(status_code=404, detail="No audit memo found. Please audit a contract first.")

    memo_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest_memo = memo_files[0]

    return FileResponse(
        path=latest_memo,
        filename=latest_memo.name,
        media_type="text/markdown",
    )


# Mount frontend static files
frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
