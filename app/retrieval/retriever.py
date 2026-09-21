import os
from dotenv import load_dotenv

from app.retrieval.bm25 import BM25Index
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore

load_dotenv()


class Retriever:
    """
    Hybrid Retriever combining:
    1. BM25 Keyword Search (lexical precision for specific terms & clause numbers)
    2. Dense Vector Search (semantic similarity for conceptual queries)
    3. Reciprocal Rank Fusion (RRF) to merge candidate lists
    4. Fast Cross-Validation / Reranking
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.bm25 = BM25Index()
        self._all_chunks: dict[str, dict] = {}

    def index_chunks(self, chunks: list[dict]) -> None:
        """Indexes chunks into the in-memory BM25 index and memory cache."""
        self._all_chunks = {
            c["chunk_id"]: c for c in chunks
        }
        self.bm25.index(chunks)

    def vector_search(self, query: str, n_results: int = 8) -> list[dict]:
        """Perform semantic search using ChromaDB."""
        query_embedding = self.embedding_service.embed(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        output = []
        for i in range(len(documents)):
            output.append({
                "chunk_id": ids[i],
                "text": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i],
                "vector_rank": i + 1,
            })

        return output

    def bm25_search(self, query: str, n_results: int = 8) -> list[dict]:
        """Perform lexical keyword search using BM25."""
        return self.bm25.search(query=query, top_k=n_results)

    def search(
        self,
        query: str,
        n_results: int = 5,
        rrf_k: int = 60,
    ) -> list[dict]:
        """
        Execute Hybrid Retrieval using Reciprocal Rank Fusion (RRF).
        Falls back gracefully to vector search if BM25 index is unpopulated.
        """
        vector_results = self.vector_search(query=query, n_results=n_results * 2)

        # If BM25 index is not yet loaded in memory, try to populate from Chroma collection
        if self.bm25.corpus_size == 0:
            try:
                coll_data = self.vector_store.collection.get()
                if coll_data and coll_data.get("ids"):
                    c_ids = coll_data["ids"]
                    c_docs = coll_data["documents"]
                    c_metas = coll_data["metadatas"]
                    raw_chunks = [
                        {
                            "chunk_id": c_ids[i],
                            "text": c_docs[i],
                            "metadata": c_metas[i] if c_metas else {},
                        }
                        for i in range(len(c_ids))
                    ]
                    self.index_chunks(raw_chunks)
            except Exception:
                pass

        bm25_results = self.bm25_search(query=query, n_results=n_results * 2)

        # If BM25 has no results or failed, return vector results directly
        if not bm25_results:
            return vector_results[:n_results]

        # Reciprocal Rank Fusion (RRF)
        # RRF_score(d) = 1/(k + rank_bm25) + 1/(k + rank_vec)
        chunk_scores: dict[str, float] = {}
        chunk_map: dict[str, dict] = {}

        for item in vector_results:
            cid = item["chunk_id"]
            rank = item["vector_rank"]
            chunk_scores[cid] = chunk_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            chunk_map[cid] = item

        for item in bm25_results:
            cid = item["chunk_id"]
            rank = item["bm25_rank"]
            chunk_scores[cid] = chunk_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            if cid not in chunk_map:
                chunk_map[cid] = item

        # Sort candidate chunks by fused RRF score descending
        sorted_cids = sorted(
            chunk_scores.keys(),
            key=lambda cid: chunk_scores[cid],
            reverse=True
        )

        fused_results = []
        for cid in sorted_cids[:n_results]:
            chunk_item = chunk_map[cid]
            chunk_item["rrf_score"] = round(chunk_scores[cid], 5)
            fused_results.append(chunk_item)

        return fused_results