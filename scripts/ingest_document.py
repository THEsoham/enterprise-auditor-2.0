import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json

from app.ingestion.pdf_loader import load_pdf


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/ingest_document.py <pdf_path>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])

    pages = load_pdf(pdf_path)

    output_path = Path("data/extracted") / f"{pdf_path.stem}_extracted.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(pages, file, indent=2, ensure_ascii=False)

    print(f"Extracted {len(pages)} pages.")
    print(f"Saved extracted text to: {output_path}")


if __name__ == "__main__":
    main()