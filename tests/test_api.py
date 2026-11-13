import json

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The API with temporary folders and a fake audit, so no AI calls are made."""
    documents, reports = tmp_path / "documents", tmp_path / "reports"
    documents.mkdir()
    reports.mkdir()
    monkeypatch.setattr(main, "DOCUMENTS_DIR", documents)
    monkeypatch.setattr(main, "REPORTS_DIR", reports)

    audits = []
    formats = []

    async def fake_pipeline(pdf_path, max_probes, display_name=None, source_format=None):
        audits.append(pdf_path)
        formats.append(source_format)
        report = {"document_name": pdf_path.name, "display_name": display_name, "findings": [{"title": "x"}]}
        (reports / f"{pdf_path.stem}_audit.json").write_text(json.dumps(report), encoding="utf-8")
        return {"report": report}

    async def fake_index(pdf_path):
        pass

    monkeypatch.setattr(main, "_run_pipeline", fake_pipeline)
    monkeypatch.setattr(main, "_ensure_indexed", fake_index)

    test_client = TestClient(main.app)
    test_client.audits = audits
    test_client.formats = formats
    test_client.reports = reports
    return test_client


def _pdf(text=None):
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def _upload(client, name, content):
    return client.post("/api/upload", files={"file": (name, content, "application/pdf")})


def test_rejects_pdf_without_text(client):
    """Scanned or blank PDFs get a clear error before any AI call."""
    response = _upload(client, "scan.pdf", _pdf())
    assert response.status_code == 400
    assert "no readable text" in response.json()["detail"]
    assert client.audits == []


def test_rejects_corrupt_pdf(client):
    assert _upload(client, "broken.pdf", b"not a pdf").status_code == 400


def test_same_file_twice_reuses_the_audit(client):
    """An identical upload is not re-audited or stored twice."""
    content = _pdf("A real contract.")
    first = _upload(client, "contract.pdf", content)
    second = _upload(client, "contract.pdf", content)

    assert first.status_code == second.status_code == 200
    assert len(client.audits) == 1
    assert second.json()["report"]["document_name"] == "contract.pdf"


def test_different_file_with_same_name_gets_its_own_audit(client):
    _upload(client, "contract.pdf", _pdf("Version one."))
    response = _upload(client, "contract.pdf", _pdf("Version two."))

    assert len(client.audits) == 2
    assert client.audits[0] != client.audits[1]
    assert response.json()["report"]["display_name"] == "contract.pdf"


def test_failed_audit_is_not_reused(client):
    """A report with no findings, e.g. from an API outage, is audited again."""
    content = _pdf("A real contract.")
    _upload(client, "contract.pdf", content)
    report_path = client.reports / "contract_audit.json"
    report_path.write_text(json.dumps({"findings": []}), encoding="utf-8")

    _upload(client, "contract.pdf", content)
    assert len(client.audits) == 2


def test_memo_download_returns_the_requested_contract(client):
    (client.reports / "first_audit_memo.md").write_text("first memo", encoding="utf-8")
    (client.reports / "second_audit_memo.md").write_text("second memo", encoding="utf-8")

    assert client.get("/api/download/memo", params={"document": "first.pdf"}).text == "first memo"
    assert client.get("/api/download/memo", params={"document": "second.pdf"}).text == "second memo"
    assert client.get("/api/download/memo", params={"document": "missing.pdf"}).status_code == 404
    assert client.get("/api/download/memo").status_code == 422


def test_memo_download_blocks_path_traversal(client, tmp_path):
    (tmp_path / "secret_audit_memo.md").write_text("secret", encoding="utf-8")
    response = client.get("/api/download/memo", params={"document": "../secret.pdf"})
    assert response.status_code == 404


def _upload_as(client, name, content, content_type):
    return client.post("/api/upload", files={"file": (name, content, content_type)})


def test_converted_files_tell_the_pipeline_their_original_format(client):
    """Tables and signatures are skipped for converted files, so the pipeline must know."""
    _upload(client, "contract.pdf", _pdf("A real contract."))
    _upload_as(client, "notes.txt", b"A plain text contract.", "text/plain")

    assert client.formats == [None, ".txt"]


def test_windows_text_file_keeps_its_special_characters(client):
    """A Notepad file saved as Windows-1252 must not lose euro signs, dashes or curly quotes."""
    text = "Fee: \u20ac100 \u2013 \u201cnet 30\u201d caf\u00e9"
    response = _upload_as(client, "terms.txt", text.encode("cp1252"), "text/plain")
    assert response.status_code == 200

    converted = next(client.audits[0].parent.glob("terms_*_converted.pdf"))
    with pymupdf.open(converted) as doc:
        extracted = doc[0].get_text("text")
    assert "\u20ac100" in extracted and "\u201cnet 30\u201d" in extracted and "caf\u00e9" in extracted


def test_rupee_sign_survives_conversion(client):
    response = _upload_as(client, "fees.txt", "Monthly fee: \u20b95,000".encode("utf-8"), "text/plain")
    assert response.status_code == 200

    converted = next(client.audits[0].parent.glob("fees_*_converted.pdf"))
    with pymupdf.open(converted) as doc:
        assert "\u20b95,000" in doc[0].get_text("text")


def test_utf16_text_file_is_read(client):
    response = _upload_as(client, "wide.txt", "Fee: \u20b95,000".encode("utf-16"), "text/plain")
    assert response.status_code == 200
    converted = next(client.audits[0].parent.glob("wide_*_converted.pdf"))
    with pymupdf.open(converted) as doc:
        assert "\u20b95,000" in doc[0].get_text("text")
