import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.retriever import Retriever


def main() -> None:
    query = "What are the Provider's termination rights?"

    retriever = Retriever()

    results = retriever.search(
        query=query,
        n_results=3,
    )

    print("\nQUERY:")
    print(query)

    print("\nRESULTS:")
    
    for i, result in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"RESULT {i}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Page: {result['metadata'].get('page_number')}")
        print(f"Section: {result['metadata'].get('section')}")
        print(f"Distance: {result['distance']}")
        print("\nTEXT:")
        print(result["text"])


if __name__ == "__main__":
    main()