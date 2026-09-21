from pathlib import Path

import chromadb


class VectorStore:

    def __init__(
        self,
        persist_directory: str = "data/indexes/chroma",
        collection_name: str = "enterprise_auditor"
    ):
        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def reset(self) -> None:
        self.client.delete_collection(
            self.collection.name
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection.name
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]]
    ) -> None:

        self.collection.upsert(
            ids=[
                chunk["chunk_id"]
                for chunk in chunks
            ],

            documents=[
                chunk["text"]
                for chunk in chunks
            ],

            embeddings=embeddings,

            metadatas=[
                {
                    "page_number": chunk["page_number"],
                    "section": chunk.get("section") or "",
                    "source": chunk["metadata"].get(
                        "source",
                        "pdf"
                    ),
                }
                for chunk in chunks
            ],
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5
    ) -> dict:

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )