import re

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


def split_large_text(text: str, max_chars: int) -> list[str]:
    """Split oversized text without cutting sentences when possible."""

    if len(text) <= max_chars:
        return [text.strip()]

    sentences = re.split(r"(?<=[.!?])\s+", text)

    pieces = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

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

    for page in pages:

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