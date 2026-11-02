import re

from app.auditing.obligation_extractor import merge_abbreviations
from app.chunking.chunk_models import DocumentChunk


# Matches major section headings such as:
# 10. TERMINATION
# 11. NON-SOLICITATION
# 14. TERM AND RENEWAL
#
# It intentionally does NOT match:
# 10.3 Provider may terminate...


SECTION_PATTERN = re.compile(
    r"(?<![\d.])"
    r"(\d{1,2})\.\s+"
    r"([A-Z][A-Z &\-]{2,})"
    r"(?=\s|$)"
)

# A page ending in one of these words has clearly not finished its sentence
UNFINISHED_ENDING = re.compile(r"(?:,|\b(?:the|a|an|of|to|and|or|by|for|in|on|upon|with|at|from|that|its))$", re.IGNORECASE)
SENTENCE_START = re.compile(r"[.;:!?]\s+")


def rejoin_split_sentences(pages: list[dict]) -> list[dict]:
    """
    Chunks are made page by page, so a sentence running onto the next page would
    be cut in two, and a quote of it could never pass the exact quote check.
    Move the unfinished start of such a sentence onto the page where it ends.
    """
    pages = [dict(page) for page in pages]

    for page, next_page in zip(pages, pages[1:]):
        text = page["text"].rstrip()
        following = next_page["text"].lstrip()
        if not text or not following or text[-1] in ".;:!?)":
            continue

        continues = following[0].islower() or UNFINISHED_ENDING.search(text)
        if not continues or SECTION_PATTERN.match(following):
            continue

        # The unfinished part starts after the last sentence ending or line of its own clause
        starts = [m.end() for m in SENTENCE_START.finditer(text)]
        start = starts[-1] if starts else 0
        page["text"] = text[:start].rstrip()
        next_page["text"] = f"{text[start:].strip()} {following}"

    return pages


def split_large_text(text: str, max_chars: int) -> list[str]:
    """Split oversized text without cutting sentences when possible."""

    if len(text) <= max_chars:
        return [text.strip()]

    sentences = merge_abbreviations(re.split(r"(?<=[.!?])\s+", text))

    pieces = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # A single sentence over the limit can only be split between words
        while len(sentence) > max_chars:
            if current:
                pieces.append(current.strip())
                current = ""
            cut = sentence.rfind(" ", 0, max_chars)
            cut = cut if cut > 0 else max_chars
            pieces.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()

        if current and len(current) + len(sentence) + 1 > max_chars:
            pieces.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        pieces.append(current.strip())

    return pieces


def split_sections(text: str) -> list[tuple[str | None, str]]:
    """
    Split a page/document into major numbered sections.

    Example:

    9. LIABILITY...
    ...
    10. TERMINATION
    ...

    becomes:

    ("9. LIABILITY", "...")
    ("10. TERMINATION", "...")
    """

    matches = list(SECTION_PATTERN.finditer(text))

    if not matches:
        return [(None, text.strip())]

    sections = []

    # Text before the first detected section
    if matches[0].start() > 0:
        prefix = text[:matches[0].start()].strip()

        if prefix:
            sections.append((None, prefix))

    for index, match in enumerate(matches):
        section_number = match.group(1)
        section_title = match.group(2).strip()

        section_name = f"{section_number}. {section_title}"

        start = match.start()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        section_text = text[start:end].strip()

        if section_text:
            sections.append((section_name, section_text))

    return sections


def chunk_pages(
    pages: list[dict],
    max_chars: int = 1800
) -> list[DocumentChunk]:

    chunks = []
    chunk_counter = 1

    active_section = None

    for page in rejoin_split_sentences(pages):

        page_number = page["page_number"]
        text = page["text"].strip()

        if not text:
            continue

        sections = split_sections(text)

        for section_name, section_text in sections:

            # If this page continues a section from the previous page
            if section_name is None:
                section_name = active_section

            if section_name is not None:
                active_section = section_name

            pieces = split_large_text(
                section_text,
                max_chars
            )

            for piece in pieces:

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chunk-{chunk_counter:04d}",
                        page_number=page_number,
                        text=piece,
                        section=section_name,
                        metadata={
                            "source": "pdf",
                            "page_number": page_number,
                            "section": section_name or "",
                        },
                    )
                )

                chunk_counter += 1

    return chunks