import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore


def main() -> None:

    print("Starting index build...")

    if len(sys.argv) != 2:
        print("Usage: python scripts/build_index.py <chunks_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    print(f"Reading: {input_path}")

    if not input_path.exists():
        print(f"ERROR: File does not exist: {input_path}")
        sys.exit(1)

    with input_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Loaded {len(chunks)} chunks.")

    embedding_service = EmbeddingService()

    vector_store = VectorStore()

    print("Resetting vector collection...")
    vector_store.reset()

    embeddings = []

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"Embedding {index}/{len(chunks)} "
            f"({chunk['chunk_id']})..."
        )

        embedding = embedding_service.embed(
            chunk["text"]
        )

        embeddings.append(embedding)

    print("Adding chunks to vector store...")

    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings
    )

    print("Vector index created successfully.")
    print(
        f"Stored documents: "
        f"{vector_store.collection.count()}"
    )


if __name__ == "__main__":
    main()