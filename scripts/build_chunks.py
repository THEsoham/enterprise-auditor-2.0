import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.chunking.semantic_chunker import chunk_pages


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/build_chunks.py <extracted_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    with input_path.open("r", encoding="utf-8") as file:
        pages = json.load(file)

    chunks = chunk_pages(pages)

    output_path = Path("data/chunks") / f"{input_path.stem}_chunks.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            [chunk.model_dump() for chunk in chunks],
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Created {len(chunks)} chunks.")
    print(f"Saved chunks to: {output_path}")


if __name__ == "__main__":
    main()