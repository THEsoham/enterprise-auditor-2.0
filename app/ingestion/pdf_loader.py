from pathlib import Path

import pymupdf


def load_pdf(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF while preserving page numbers.

    Returns:
        [
            {
                "page_number": 1,
                "text": "Extracted text..."
            }
        ]
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file must be a PDF.")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            text = page.get_text("text").strip()

            pages.append(
                {
                    "page_number": page_index + 1,
                    "text": text,
                }
            )

    return pages