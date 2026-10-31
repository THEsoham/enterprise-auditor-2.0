import re


# Typographic characters PDFs use that LLMs usually rewrite as plain ASCII
_PUNCTUATION_MAP = str.maketrans({
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    " ": " ",
})

MIN_QUOTE_CHARS = 8


def normalize(text: str) -> str:
    """Lowercase, unify punctuation, and collapse whitespace/line wraps."""
    text = str(text or "").translate(_PUNCTUATION_MAP).lower()
    return re.sub(r"\s+", " ", text).strip()


def quote_in_text(quote: str, text: str) -> bool:
    """
    True when the quote appears verbatim in the text (ignoring case, whitespace
    and curly quotes). Ellipses are allowed: every fragment between "..." must
    appear in order.
    """
    q = normalize(quote).strip(" \"'")
    if len(q) < MIN_QUOTE_CHARS:
        return False

    haystack = normalize(text)
    fragments = [f.strip(" .,;:") for f in re.split(r"\.{3}|…", q)]
    fragments = [f for f in fragments if f]
    if not fragments:
        return False

    position = 0
    for fragment in fragments:
        index = haystack.find(fragment, position)
        if index < 0:
            return False
        position = index + len(fragment)

    return True


def ground_evidence(finding: dict, evidence: list[dict]) -> dict:
    """
    Deterministically checks every quote in a finding against the retrieved
    contract chunks. Grounded quotes get their chunk ID, page, and section
    corrected to the chunk where the text was actually found.
    """
    grounded = []
    ungrounded = []

    for item in finding.get("evidence") or []:
        if not isinstance(item, dict):
            continue

        quote = item.get("quote", "")
        match = next(
            (c for c in evidence if quote_in_text(quote, c.get("text", ""))),
            None,
        )

        if match:
            metadata = match.get("metadata") or {}
            grounded.append({
                **item,
                "chunk_id": match.get("chunk_id", item.get("chunk_id")),
                "page": metadata.get("page_number", item.get("page")),
                "section": metadata.get("section") or item.get("section"),
                "grounded": True,
            })
        else:
            ungrounded.append(item)

    return {
        "grounded": grounded,
        "ungrounded": ungrounded,
    }
