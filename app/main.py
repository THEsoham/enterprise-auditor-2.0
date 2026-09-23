import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.pipeline.audit_pipeline import AuditPipeline
from app.debate.debate_graph import DebateEngine
from app.scoring.risk_scorer import RiskScorer

PROJECT_ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Enterprise Auditor 2.0 API",
    description="Autonomous Contract Auditing, AI Courtroom, and Visual Scanner",
    version="2.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    query: str


class AuditRequest(BaseModel):
    filename: Optional[str] = "sample_contract.pdf"
    max_probes: Optional[int] = 7


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "system": "Enterprise Auditor 2.0",
        "models": {
            "auditor": "OpenAI gpt-4o-mini",
            "verifier": "Gemini 3.6 Flash",
        }
    }


@app.get("/api/report/latest")
async def get_latest_report():
    """Retrieve the baseline audit report JSON."""
    report_dir = PROJECT_ROOT / "data" / "reports"
    sample_files = list(report_dir.glob("sample_contract_audit.json"))
    if sample_files:
        with open(sample_files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    raise HTTPException(status_code=404, detail="No audit report found.")


@app.get("/api/sample/demo")
async def get_sample_demo_report():
    """Load the pre-computed sample contract audit on demand for demonstration."""
    report_dir = PROJECT_ROOT / "data" / "reports"
    sample_files = list(report_dir.glob("sample_contract*_audit.json"))
    if sample_files:
        sample_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        with open(sample_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"report": data}

    pdf_path = PROJECT_ROOT / "data" / "documents" / "sample_contract.pdf"
    if pdf_path.exists():
        pipeline = AuditPipeline(max_debate_rounds=2)
        res = await asyncio.to_thread(pipeline.audit, pdf_path=pdf_path, max_probes=5)
        return {"report": res["report"]}

    raise HTTPException(status_code=404, detail="Sample contract not found.")


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new contract PDF/text document and run the autonomous audit pipeline."""
    allowed_exts = (".pdf", ".txt", ".docx", ".md")
    ext = Path(file.filename).suffix.lower()
    if not ext.endswith(allowed_exts):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: PDF, TXT, DOCX, MD."
        )

    dest_dir = PROJECT_ROOT / "data" / "documents"
    dest_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(file.filename).stem
    dest_path = dest_dir / file.filename
    if dest_path.exists():
        import time
        timestamp = int(time.time())
        dest_path = dest_dir / f"{stem}_{timestamp}{ext}"

    content = await file.read()

    # If file is text/md/docx, convert to a valid PDF for the pipeline
    if ext in (".txt", ".md", ".docx"):
        pdf_path = dest_dir / f"{stem}_converted.pdf"
        try:
            import fitz
            doc = fitz.open()
            page = doc.new_page()
            text_str = content.decode("utf-8", errors="ignore")
            # Wrap long text into PDF page
            page.insert_text((50, 50), text_str[:4000], fontsize=11)
            doc.save(pdf_path)
            doc.close()
            dest_path = pdf_path
        except Exception as conv_err:
            print(f"Text to PDF conversion warning: {conv_err}")
            # Write raw content to file anyway
            with open(dest_path, "wb") as buffer:
                buffer.write(content)
    else:
        with open(dest_path, "wb") as buffer:
            buffer.write(content)

    try:
        pipeline = AuditPipeline(max_debate_rounds=2)
        result = await asyncio.to_thread(
            pipeline.audit,
            pdf_path=dest_path,
            max_probes=7,
        )
        return {
            "status": "success",
            "filename": file.filename,
            "report": result["report"],
            "message": f"Successfully audited {file.filename}",
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Audit failed for {file.filename}: {str(e)}")



@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    """Execute autonomous audit pipeline on the specified contract PDF."""
    pdf_path = PROJECT_ROOT / "data" / "documents" / req.filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Contract not found: {req.filename}")

    pipeline = AuditPipeline(max_debate_rounds=2)
    result = await asyncio.to_thread(
        pipeline.audit,
        pdf_path=pdf_path,
        max_probes=req.max_probes,
    )
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

    engine = DebateEngine(max_rounds=2)
    result = await asyncio.to_thread(engine.run, query=query)

    finding = result.get("finding") or {}
    verification = result.get("verification") or {}
    history = result.get("history") or []

    scorer = RiskScorer()
    verdict = str(verification.get("verdict", "ACCEPTED")).upper()
    bucket = scorer.classify_bucket(
        finding=finding,
        verdict=verdict,
        severity=finding.get("severity", "medium"),
        final_score=80.0
    )
    plain_english, why_flagged, suggested_negotiation = scorer.generate_plain_english(
        finding=finding,
        bucket=bucket
    )
    clause_balance = scorer.detect_clause_balance(finding)

    finding["bucket"] = bucket
    finding["plain_english"] = plain_english
    finding["why_flagged"] = why_flagged
    finding["suggested_negotiation"] = suggested_negotiation
    finding["clause_balance"] = clause_balance.model_dump()

    return {
        "query": query,
        "verdict": verdict,
        "status": result.get("final_status", "ACCEPTED"),
        "finding": finding,
        "verification": verification,
        "history": history,
        "plain_english": plain_english,
        "why_flagged": why_flagged,
        "suggested_negotiation": suggested_negotiation,
        "clause_balance": clause_balance.model_dump(),
        "evidence": finding.get("evidence", []),
    }


@app.get("/api/download/memo")
async def download_audit_memo():
    """Download the executive Markdown audit memo for the latest audited contract."""
    report_dir = PROJECT_ROOT / "data" / "reports"
    memo_files = list(report_dir.glob("*_audit_memo.md"))
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
