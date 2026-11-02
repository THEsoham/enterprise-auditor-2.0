import re
from pathlib import Path
from typing import Literal, Optional
import pymupdf
from pydantic import BaseModel, Field


ExecutionState = Literal["FULLY_EXECUTED", "PARTIALLY_EXECUTED", "UNEXECUTED_DRAFT"]

# A party's signing block starts with a line such as "For Northstar Analytics Pvt. Ltd."
BLOCK_HEADING = re.compile(r"^(?:Signed\s+)?(?:For|On behalf of)\s+(?:and on behalf of\s+)?([A-Z][A-Za-z0-9\s,\.\-&]{2,60}?):?$")
SIGNATURE_LINE = re.compile(r"^Signature\s*:\s*(.*)$", re.IGNORECASE)


class PartySignatureStatus(BaseModel):
    party_role: str
    party_name: str
    signatory_name: str = "Unfilled"
    signatory_title: str = "Unfilled"
    signatory_date: str = "Unfilled"
    signature_detected: bool = False
    status_label: str = "NOT DETECTED"


class DocumentExecutionReport(BaseModel):
    overall_status: ExecutionState
    headline: str
    signature_page: Optional[int] = None
    parties: list[PartySignatureStatus] = Field(default_factory=list)
    visual_notes: str = ""
    disclaimer: str = "Visual status detection only; does not constitute legal verification of signature validity."


class SignatureAnalyzer:
    """
    Visual and structural analyzer for document execution blocks.
    Finds each party's signing block on the page and checks that block on its
    own, so one party can be signed while the other is not. A block counts as
    signed when it contains a signature image, hand-drawn ink, or text typed on
    the signature line. Anything outside the blocks, such as a logo, is ignored.
    """

    def analyze(self, pdf_path: str | Path, parties: Optional[dict[str, str]] = None) -> DocumentExecutionReport:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        found_page_num: Optional[int] = None
        parties_detected: list[PartySignatureStatus] = []

        with pymupdf.open(pdf_path) as doc:
            # Look backwards from the last pages where execution blocks typically live
            for page_index in range(len(doc) - 1, -1, -1):
                page = doc[page_index]
                text = page.get_text("text")

                if "SIGNATURES" in text or "IN WITNESS WHEREOF" in text or "Signature:" in text:
                    found_page_num = page_index + 1
                    parties_detected = self._read_blocks(page, parties or {})
                    break

        if not found_page_num:
            return DocumentExecutionReport(
                overall_status="UNEXECUTED_DRAFT",
                headline="⚠️ NO SIGNATURE BLOCK DETECTED — Document may be an informal schedule or incomplete draft",
                signature_page=None,
                parties=[],
                visual_notes="No standard execution block (SIGNATURES / IN WITNESS WHEREOF) was detected in the document.",
            )

        signed = [p for p in parties_detected if p.signature_detected]
        unsigned = [p for p in parties_detected if not p.signature_detected]

        if parties_detected and not unsigned:
            overall_status = "FULLY_EXECUTED"
            headline = f"✓ FULLY EXECUTED — Signatures visually detected for all parties on Page {found_page_num}"
            visual_notes = f"All {len(signed)} party execution blocks contain visual signature representations."
        elif signed:
            overall_status = "PARTIALLY_EXECUTED"
            headline = f"⚠️ PARTIALLY EXECUTED — Signatures detected for {len(signed)} of {len(parties_detected)} parties on Page {found_page_num}"
            visual_notes = "Not signed: " + ", ".join(f"{p.party_role} ({p.party_name})" for p in unsigned) + "."
        else:
            overall_status = "UNEXECUTED_DRAFT"
            headline = f"⚠️ SIGNATURE STATUS: NOT DETECTED (DRAFT) — Blank signature lines on Page {found_page_num}"
            names = " and ".join(f"{p.party_role} ({p.party_name})" for p in parties_detected) or "the parties"
            visual_notes = (
                f"Page {found_page_num} contains a signature section for {names}. "
                "No signature images, hand-drawn marks, or typed signatures were detected."
            )

        return DocumentExecutionReport(
            overall_status=overall_status,
            headline=headline,
            signature_page=found_page_num,
            parties=parties_detected,
            visual_notes=visual_notes,
        )

    def _read_blocks(self, page, parties: dict[str, str]) -> list[PartySignatureStatus]:
        lines = self._text_lines(page)
        headings = [
            (rect, match.group(1).strip(" ,"))
            for rect, text in lines
            for match in [BLOCK_HEADING.match(text)]
            if match
        ][:2]

        results = []
        for index, (rect, name) in enumerate(headings):
            area = self._block_area(page, rect, index, headings)
            role = self._role_for(name, index, parties)
            block_lines = [text for line_rect, text in lines if self._inside(line_rect, area)]
            signed = self._has_ink(page, area) or self._has_typed_signature(block_lines)

            results.append(PartySignatureStatus(
                party_role=role,
                party_name=name,
                signatory_name=self._field(block_lines, "Name"),
                signatory_title=self._field(block_lines, "Title"),
                signatory_date=self._field(block_lines, "Date"),
                signature_detected=signed,
                status_label="SIGNED" if signed else "NOT DETECTED",
            ))
        return results

    @staticmethod
    def _text_lines(page) -> list[tuple[pymupdf.Rect, str]]:
        lines = []
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                if text:
                    lines.append((pymupdf.Rect(line["bbox"]), text))
        return lines

    @staticmethod
    def _block_area(page, rect, index: int, headings: list) -> pymupdf.Rect:
        """A block runs from its heading to the next heading: beside it in a table, or below it."""
        other = headings[1 - index][0] if len(headings) == 2 else None
        side_by_side = other is not None and abs(other.y0 - rect.y0) < rect.height

        if side_by_side:
            middle = (rect.x0 + other.x0) / 2
            left, right = (0, middle) if rect.x0 < other.x0 else (middle, page.rect.width)
            return pymupdf.Rect(left, rect.y0, right, page.rect.height)

        bottom = other.y0 if other is not None and other.y0 > rect.y0 else page.rect.height
        return pymupdf.Rect(0, rect.y0, page.rect.width, bottom)

    @staticmethod
    def _inside(rect, area) -> bool:
        x, y = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
        return area.x0 <= x <= area.x1 and area.y0 <= y <= area.y1

    def _has_ink(self, page, area) -> bool:
        for info in page.get_image_info():
            if self._inside(pymupdf.Rect(info["bbox"]), area):
                return True

        # Hand-drawn signatures are curves; table borders and blank lines are straight
        for drawing in page.get_drawings():
            is_curved = any(item[0] == "c" for item in drawing.get("items", []))
            if is_curved and self._inside(drawing["rect"], area):
                return True
        return False

    @staticmethod
    def _has_typed_signature(block_lines: list[str]) -> bool:
        for text in block_lines:
            match = SIGNATURE_LINE.match(text)
            if match and match.group(1).strip(" _"):
                return True
        return False

    @staticmethod
    def _field(block_lines: list[str], label: str) -> str:
        for text in block_lines:
            match = re.match(rf"^{label}\s*:\s*(.*)$", text, re.IGNORECASE)
            if match:
                value = match.group(1).strip(" _")
                return value or "[Blank underline]"
        return "Unfilled"

    @staticmethod
    def _role_for(name: str, index: int, parties: dict[str, str]) -> str:
        """Match the block to the contract's parties; signing order is only the last resort."""
        lowered = name.lower()
        for key, role in (("customer", "Customer"), ("provider", "Provider")):
            party_name = str(parties.get(key) or "").lower()
            first_word = party_name.split()[0] if party_name else ""
            if role.lower() in lowered or (first_word and first_word in lowered):
                return role
        return "Customer" if index == 0 else "Provider"
