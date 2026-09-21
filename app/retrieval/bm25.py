import math
import re
from collections import Counter


# Standard English stopwords to eliminate noise in BM25 scoring
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric words, filtering stopwords."""
    words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]


class BM25Index:
    """
    In-memory Okapi BM25 index for exact keyword and clause retrieval.
    Parametrized with standard k1 = 1.5, b = 0.75.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0.0
        self.doc_lengths = []
        self.doc_ids = []
        self.doc_texts = []
        self.doc_metadatas = []
        self.term_freqs = []
        self.df = Counter()
        self.idf = {}

    def index(self, chunks: list[dict]) -> None:
        """Index a list of chunks: dict with chunk_id, text, metadata."""
        self.doc_ids = []
        self.doc_texts = []
        self.doc_metadatas = []
        self.term_freqs = []
        self.doc_lengths = []
        self.df = Counter()
        self.corpus_size = len(chunks)

        if self.corpus_size == 0:
            return

        total_length = 0

        for chunk in chunks:
            cid = chunk.get("chunk_id", "")
            text = chunk.get("text", "")
            meta = chunk.get("metadata", {})

            tokens = tokenize(text)
            doc_len = len(tokens)

            self.doc_ids.append(cid)
            self.doc_texts.append(text)
            self.doc_metadatas.append(meta)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            tf = Counter(tokens)
            self.term_freqs.append(tf)

            for term in tf.keys():
                self.df[term] += 1

        self.avgdl = total_length / self.corpus_size if self.corpus_size > 0 else 0.0

        # Calculate IDF with smoothing
        self.idf = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log(
                (self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0
            )

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search BM25 index and return scored chunks."""
        if self.corpus_size == 0:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores = []

        for idx in range(self.corpus_size):
            doc_len = self.doc_lengths[idx]
            tf = self.term_freqs[idx]
            score = 0.0

            len_norm = 1.0 - self.b + self.b * (doc_len / (self.avgdl or 1.0))

            for term in q_tokens:
                if term not in tf:
                    continue
                term_tf = tf[term]
                term_idf = self.idf.get(term, 0.0)

                numerator = term_tf * (self.k1 + 1.0)
                denominator = term_tf + self.k1 * len_norm
                score += term_idf * (numerator / denominator)

            scores.append((idx, score))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for rank, (idx, score) in enumerate(scores[:top_k], start=1):
            if score <= 0.0:
                continue
            results.append({
                "chunk_id": self.doc_ids[idx],
                "text": self.doc_texts[idx],
                "metadata": self.doc_metadatas[idx],
                "bm25_score": round(score, 4),
                "bm25_rank": rank,
            })

        return results
