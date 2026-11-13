"""
Reads a DOCX file directly, without converting it to PDF first.

A DOCX is a zip of XML files; the body lives in word/document.xml. Paragraphs are
<w:p> elements and tables are <w:tbl> elements made of rows (<w:tr>) and cells (<w:tc>).
Reading the XML keeps tables as real rows and columns, which a text-to-PDF
conversion flattens into loose lines.
"""

import io
import zipfile
import xml.etree.ElementTree as ET

from app.ingestion.table_extractor import TableData, TableExtractor

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# DOCX files have no fixed pages, so tables from them carry this page number
NO_PAGE = 0


def _body(content: bytes) -> ET.Element:
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{W}body")
    return body if body is not None else root


def _text(element: ET.Element) -> str:
    """Text of a paragraph or cell, keeping tabs and line breaks as spaces."""
    parts = []
    for node in element.iter():
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag in (f"{W}tab", f"{W}br", f"{W}cr"):
            parts.append(" ")
    return "".join(parts).strip()


def _rows(table: ET.Element) -> list[list[str]]:
    """Rows of a table; text of a nested table stays inside the cell that holds it."""
    rows = []
    for row in table.findall(f"{W}tr"):
        cells = [" ".join(filter(None, (_text(p) for p in cell.iter(f"{W}p")))) for cell in row.findall(f"{W}tc")]
        if any(cells):
            rows.append(cells)
    return rows


def docx_to_text(content: bytes) -> str:
    """
    Body text in reading order: one line per paragraph, and one line per table row
    with its cells separated by " | ", so each row stays together when chunked.
    """
    lines = []
    for block in _body(content):
        if block.tag == f"{W}p":
            text = _text(block)
            if text:
                lines.append(text)
        elif block.tag == f"{W}tbl":
            lines.extend(" | ".join(cells) for cells in _rows(block))
    return "\n".join(lines)


def extract_docx_tables(content: bytes) -> list[TableData]:
    """Tables in a DOCX, classified and risk-checked the same way as PDF tables."""
    analyzer = TableExtractor()
    tables = []
    for index, block in enumerate((b for b in _body(content) if b.tag == f"{W}tbl"), start=1):
        rows = _rows(block)
        if not rows:
            continue
        headers, body = rows[0], rows[1:]
        table_type = analyzer._classify_table(headers)
        risks = analyzer._analyze_pricing_risks(headers, body, NO_PAGE) if table_type == "pricing_tiers" else []
        tables.append(TableData(
            table_id=f"table-docx-{index}",
            page_number=NO_PAGE,
            table_type=table_type,
            headers=headers,
            rows=body,
            markdown=analyzer._to_markdown(headers, body),
            risks=risks,
        ))
    return tables
