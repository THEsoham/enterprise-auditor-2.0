import re
from pathlib import Path
import pdfplumber
from pydantic import BaseModel, Field


# Fonts that hold symbols rather than letters
SYMBOL_FONTS = ("dingbat", "symbol", "rupee", "wingding")


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
        if "signature" in h_str or any(h.startswith("for ") for h in headers_lower):
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
            clean_cells = [
                self._clean_cell(row[i]) if i < len(row) else ""
                for i in range(col_count)
            ]
            md += "| " + " | ".join(clean_cells) + " |\n"

        return md.strip()

    @staticmethod
    def _clean_cell(value) -> str:
        if value is None:
            return ""
        return str(value).replace("\n", " ").strip()

    @staticmethod
    def _restore_rupee_signs(page) -> None:
        """
        Some PDFs draw the ₹ sign with a symbol font (e.g. ZapfDingbats), so the
        text comes out as "n85,000". Swap the character back to ₹ only when it
        really is a symbol-font glyph sitting right before a number, so a normal
        letter "n" or "I" in the contract is never touched.
        """
        chars = page.chars
        for current, following in zip(chars, chars[1:]):
            font = str(current.get("fontname", "")).lower()
            if (
                current.get("text") in {"n", "I"}
                and any(name in font for name in SYMBOL_FONTS)
                and str(following.get("text", "")).isdigit()
            ):
                current["text"] = "₹"

    @staticmethod
    def _parse_amount(cell: str) -> float | None:
        match = re.search(r"\d[\d,]*(?:\.\d+)?", cell)
        if not match:
            return None
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None

    def _analyze_pricing_risks(
        self,
        headers: list[str],
        rows: list[list[str]],
        page_number: int,
    ) -> list[dict]:
        """
        Identifies financial and operational risks embedded within pricing tables.
        (The "no price increase cap" check lives in MissingClauseDetector, so it
        also runs on contracts that state their fees in sentences, not tables.)
        """
        risks = []
        headers_lower = [str(h).lower() if h else "" for h in headers]

        overage_col = next((i for i, h in enumerate(headers_lower) if "overage" in h or "excess" in h), None)
        if overage_col is not None:
            rates = []
            for row in rows:
                if overage_col < len(row):
                    cell = self._clean_cell(row[overage_col])
                    amount = self._parse_amount(cell)
                    if amount is not None:
                        rates.append((self._clean_cell(row[0]) if row else "", cell, amount))

            if len(rates) >= 2:
                highest = max(rates, key=lambda r: r[2])
                lowest = min(rates, key=lambda r: r[2])
                if lowest[2] > 0 and highest[2] > lowest[2]:
                    pct = round((highest[2] / lowest[2] - 1) * 100)
                    risks.append({
                        "risk_title": "Overage Fee Exposure",
                        "severity": "medium",
                        "page_number": page_number,
                        "observation": (
                            f"The {highest[0]} tier overage rate ({highest[1]}) is {pct}% higher than the "
                            f"{lowest[0]} tier rate ({lowest[1]}). Usage spikes on a lower tier could cause "
                            "unpredictable invoice increases."
                        ),
                        "recommendation": (
                            "Negotiate a monthly overage cap or an automatic tier upgrade when usage "
                            "consistently exceeds the included quota."
                        ),
                    })

        return risks

    # A header cell longer than this is a paragraph, not a column name
    MAX_HEADER_CHARS = 250

    @classmethod
    def _is_text_box(cls, rows: list[list[str]]) -> bool:
        """
        A box drawn around a code sample or a paragraph has ruling lines, so pdfplumber
        reports it as a table. A real table has at least two columns with content and
        short column headers.
        """
        columns = max(len(r) for r in rows)
        filled = sum(1 for i in range(columns) if any(i < len(r) and r[i] for r in rows))
        return filled < 2 or any(len(cell) > cls.MAX_HEADER_CHARS for cell in rows[0])

    # A table whose last row is this close to the bottom of the page may continue on the next page
    PAGE_BOTTOM_MARGIN = 0.2

    @classmethod
    def _reaches_page_bottom(cls, page, found_table) -> bool:
        return found_table.bbox[3] >= page.height * (1 - cls.PAGE_BOTTOM_MARGIN)

    @staticmethod
    def _continues(previous: TableData, rows: list[list[str]], page, raw_table) -> bool:
        """True when this table, the first on its page, carries on the previous page's table."""
        columns = max(len(previous.headers), max((len(r) for r in previous.rows), default=0))
        if not rows or max(len(r) for r in rows) != columns:
            return False
        found = page.find_tables()
        # It must start near the top of the page, with no text of its own above it
        return bool(found) and found[0].bbox[1] <= page.height * 0.2

    def extract_tables(self, pdf_path: str | Path) -> list[TableData]:
        """Extracts and parses all tables from the PDF document."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        extracted_tables: list[TableData] = []
        # The last table on the previous page, if it ran to the bottom of that page
        open_table: TableData | None = None

        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                previous_open, open_table = open_table, None
                self._restore_rupee_signs(page)
                raw_tables = page.extract_tables()
                if not raw_tables:
                    continue

                for t_idx, raw_table in enumerate(raw_tables, start=1):
                    if not raw_table or len(raw_table) < 1:
                        continue

                    # Filter out empty rows; a line break inside a cell is just wrapping
                    cleaned_rows = [
                        [self._clean_cell(cell) for cell in row]
                        for row in raw_table
                        if any(cell and cell.strip() for cell in row)
                    ]

                    if not cleaned_rows or self._is_text_box(cleaned_rows):
                        continue

                    # A table at the top of a page with the same columns as a table that ran off the
                    # previous page is that table continuing, not a new one whose first row is a header
                    if t_idx == 1 and previous_open is not None and self._continues(
                        previous_open, cleaned_rows, page, raw_tables[0]
                    ):
                        continued = cleaned_rows[1:] if cleaned_rows[0] == previous_open.headers else cleaned_rows
                        previous_open.rows.extend(continued)
                        previous_open.markdown = self._to_markdown(previous_open.headers, previous_open.rows)
                        if previous_open.table_type == "pricing_tiers":
                            previous_open.risks = self._analyze_pricing_risks(
                                previous_open.headers, previous_open.rows, previous_open.page_number
                            )
                        if self._reaches_page_bottom(page, page.find_tables()[0]):
                            open_table = previous_open
                        continue

                    headers = cleaned_rows[0]
                    body_rows = cleaned_rows[1:] if len(cleaned_rows) > 1 else []

                    table_type = self._classify_table(headers)
                    markdown_str = self._to_markdown(headers, body_rows)

                    risks = []
                    if table_type == "pricing_tiers":
                        risks = self._analyze_pricing_risks(headers, body_rows, page_index)

                    table = TableData(
                        table_id=f"table-p{page_index}-{t_idx}",
                        page_number=page_index,
                        table_type=table_type,
                        headers=headers,
                        rows=body_rows,
                        markdown=markdown_str,
                        risks=risks,
                    )
                    extracted_tables.append(table)

                    found = page.find_tables()
                    if t_idx == len(raw_tables) and found and self._reaches_page_bottom(page, found[-1]):
                        open_table = table

        return extracted_tables
