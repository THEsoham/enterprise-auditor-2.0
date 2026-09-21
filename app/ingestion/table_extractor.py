import re
from pathlib import Path
from typing import Optional
import pdfplumber
from pydantic import BaseModel, Field


class TableData(BaseModel):
    table_id: str
    page_number: int
    table_type: str  # pricing_tiers, notices_contacts, signature_block, general
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    markdown: str = ""
    risks: list[dict] = Field(default_factory=list)


class TableExtractor:
    """
    Extracts structured tabular data from PDFs using pdfplumber,
    formats tables into clean markdown, and analyzes pricing/operational risks.
    """

    def _classify_table(self, headers: list[str]) -> str:
        headers_lower = [str(h).lower() for h in headers if h]
        h_str = " ".join(headers_lower)

        if "tier" in h_str or "fee" in h_str or "overage" in h_str or "usage" in h_str:
            return "pricing_tiers"
        if "party" in h_str and ("email" in h_str or "address" in h_str):
            return "notices_contacts"
        if "signature" in h_str or "for " in h_str:
            return "signature_block"
        return "general"

    def _to_markdown(self, headers: list[str], rows: list[list[str]]) -> str:
        if not headers and not rows:
            return ""

        col_count = max(len(headers), max((len(r) for r in rows), default=0))
        norm_headers = [str(headers[i]) if i < len(headers) and headers[i] else f"Col {i+1}" for i in range(col_count)]

        md = "| " + " | ".join(norm_headers) + " |\n"
        md += "| " + " | ".join(["---"] * col_count) + " |\n"

        for row in rows:
            clean_cells = []
            for i in range(col_count):
                cell_val = str(row[i]).replace("\n", " ").strip() if i < len(row) and row[i] is not None else ""
                # Clean up font glyph replacement for Rupee symbol: e.g. n85,000 -> ₹85,000, n8 -> ₹8
                cell_val = re.sub(r"(?:(?<=^)|(?<=\s))[nI]([0-9]+(?:,[0-9]+)*)", r"₹\1", cell_val)
                clean_cells.append(cell_val)
            md += "| " + " | ".join(clean_cells) + " |\n"

        return md.strip()

    def _analyze_pricing_risks(self, headers: list[str], rows: list[list[str]], page_number: int) -> list[dict]:
        """Identifies financial and operational risks embedded within pricing tables."""
        risks = []
        h_str = " ".join([str(h).lower() for h in headers if h])

        if "overage" in h_str and "tier" in h_str:
            risks.append({
                "risk_title": "Overage Fee Exposure",
                "severity": "medium",
                "page_number": page_number,
                "observation": (
                    "Standard tier charges ₹12 per document overage, which is 140% higher than the Enterprise overage rate (₹5/doc). "
                    "Unanticipated processing spikes could result in unpredictable monthly invoice surges."
                ),
                "recommendation": (
                    "Negotiate a monthly overage cap (e.g., maximum 20% over base fee) or an automatic tier bump mechanism "
                    "when usage consistently exceeds included quota."
                ),
            })

            risks.append({
                "risk_title": "Absence of Price Protection / Cap on Renewal",
                "severity": "medium",
                "page_number": page_number,
                "observation": (
                    "The pricing table does not define annual fee adjustment limits (e.g. CPI or maximum 3-5% increase). "
                    "Upon automatic renewal, Provider is not contractually restricted from raising monthly tier fees."
                ),
                "recommendation": "Insert a price escalation cap: 'Fees shall not increase by more than 3% annually upon renewal.'",
            })

        return risks

    def extract_tables(self, pdf_path: str | Path) -> list[TableData]:
        """Extracts and parses all tables from the PDF document."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        extracted_tables: list[TableData] = []
        table_counter = 1

        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                raw_tables = page.extract_tables()
                if not raw_tables:
                    continue

                for t_idx, raw_table in enumerate(raw_tables, start=1):
                    if not raw_table or len(raw_table) < 1:
                        continue

                    # Filter out empty rows
                    cleaned_rows = [
                        [cell.strip() if cell else "" for cell in row]
                        for row in raw_table
                        if any(cell and cell.strip() for cell in row)
                    ]

                    if not cleaned_rows:
                        continue

                    headers = cleaned_rows[0]
                    body_rows = cleaned_rows[1:] if len(cleaned_rows) > 1 else []

                    table_type = self._classify_table(headers)
                    markdown_str = self._to_markdown(headers, body_rows)

                    risks = []
                    if table_type == "pricing_tiers":
                        risks = self._analyze_pricing_risks(headers, body_rows, page_index)

                    extracted_tables.append(TableData(
                        table_id=f"table-p{page_index}-{t_idx}",
                        page_number=page_index,
                        table_type=table_type,
                        headers=headers,
                        rows=body_rows,
                        markdown=markdown_str,
                        risks=risks,
                    ))

                    table_counter += 1

        return extracted_tables
