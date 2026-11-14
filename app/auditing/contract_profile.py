"""
Works out what kind of document was uploaded before it is audited:

- whether it is a contract at all (a job description or a report is not),
- which kind of contract it is, so it is checked against the right clause list
  (a vehicle sale needs warranties and title, not disaster-recovery SLAs),
- whether it is an unfilled template, with blanks where the parties, price and
  dates should be. A template cannot be judged "Strong": its key terms are missing.

All of this is rule-based, so it is fast, free and gives the same answer every time.
"""

import re

from pydantic import BaseModel, Field


class ContractProfile(BaseModel):
    is_contract: bool = True
    contract_type: str = "services"  # services | sale_of_goods | general | not_a_contract
    contract_type_label: str = "Services / SaaS Agreement"
    type_cues: list[str] = Field(default_factory=list)
    is_template: bool = False
    blank_fields: int = 0
    blank_examples: list[str] = Field(default_factory=list)


TYPE_LABELS = {
    "services": "Services / SaaS Agreement",
    "sale_of_goods": "Sale of Goods Agreement",
    "general": "General Agreement",
    "not_a_contract": "Not a Contract",
}

# Words that show a document is a contract: legal formalities and binding language
CONTRACT_MARKERS = [
    r"\bthis agreement\b", r"\bthe parties\b", r"\bby and between\b", r"\bby and among\b",
    r"\bwhereas\b", r"\bin witness whereof\b", r"\bhereinafter\b", r"\bhereby agree",
    r"\bterms and conditions\b", r"\bgoverned by\b", r"\bin consideration of\b",
    r"\beffective date\b", r"\bentire agreement\b", r"\bseverab", r"\bshall\b",
]

# Cue words for each contract type; the type with the most distinct cues wins
TYPE_CUES = {
    "sale_of_goods": [
        "purchase price", "buyer", "seller", "goods", "vehicle", "conveyance of title", "title to",
        "bill of sale", "odometer", "as is", "merchantability", "down-payment", "down payment",
        "risk of loss", "delivery date", "vin",
    ],
    "services": [
        "services", "service level", "subscription", "customer data", "provider", "statement of work",
        "uptime", "subprocessor", "sub-processor", "license", "licence", "saas", "support",
        "security incident", "service credit", "renewal term",
    ],
}

# A run of underscores, or a bracketed placeholder such as [Insert Name]
PLACEHOLDER = re.compile(r"_{4,}|\[\s*(?:insert|enter|name|date|amount|address)[^\]]{0,40}\]", re.IGNORECASE)

# Blank fields needed before a document counts as an unfilled template
TEMPLATE_MIN_BLANKS = 6


def _distinct_cues(text: str, cues: list[str]) -> list[str]:
    return [cue for cue in cues if re.search(rf"\b{re.escape(cue)}\b", text)]


# Blank lines for signing (Name: ____, Date: ____) are normal in an unsigned contract
SIGNING_LABEL = re.compile(r"(?:name|title|date|dated|signature|signed|sign|by|witness|designation|place)\s*:?\s*$", re.IGNORECASE)
SIGNING_SECTION = re.compile(r"in witness whereof|signed (?:by|for and on behalf)|signatures?\s*(?:page|block)?\s*:?\s*\n", re.IGNORECASE)


def _term_blanks(text: str) -> list[re.Match]:
    """Blanks in the contract's terms: ignores the signature area and signing lines."""
    signing = SIGNING_SECTION.search(text)
    terms = text[: signing.start()] if signing else text
    blanks = []
    for match in PLACEHOLDER.finditer(terms):
        line_before = terms[: match.start()].rsplit("\n", 1)[-1]
        if SIGNING_LABEL.search(line_before):
            continue
        blanks.append(match)
    return blanks


# What a blank is for, judged from the words around it; the most specific hint is tried first
FIELD_HINTS = [
    ("delivery date", r"deliver"),
    ("jurisdiction / court", r"jurisdiction|courts? of"),
    ("governing law", r"laws? of the (?:state|country)|governed by"),
    ("price / payment amount", r"\$|dollars|rupees|\bprice\b|payment|amount|\bfee"),
    ("item details", r"\b(?:make|model|year|colou?r|body|miles|mileage|vin|odometer|serial|quantity|description)\b"),
    ("party names / addresses", r"between|among|\bseller\b|\bbuyer\b|\bparty\b|address|\bof\s*$"),
    ("dates", r"day of|\b20\s*$|\bdate"),
    ("term / duration", r"\b(?:term|days|months|years|period)\b"),
]


def _blank_examples(text: str, blanks: list[re.Match], limit: int = 6) -> list[str]:
    """Which kinds of terms are left blank, e.g. 'price / payment amount', 'delivery date'."""
    found: list[str] = []
    for match in blanks:
        line_start = text.rfind("\n", 0, match.start()) + 1
        context = PLACEHOLDER.sub(" ", text[max(line_start - 80, 0): match.start()]).lower()
        context = re.sub(r"\s+", " ", context).strip()
        for label, pattern in FIELD_HINTS:
            if re.search(pattern, context[-70:]):
                if label not in found:
                    found.append(label)
                break
    return found[:limit]


def profile_contract(full_text: str) -> ContractProfile:
    text = re.sub(r"\s+", " ", full_text or "").lower()

    markers = sum(1 for m in CONTRACT_MARKERS if re.search(m, text))
    shall_count = len(re.findall(r"\bshall\b", text))
    # A contract binds parties: it has formalities AND repeated binding language.
    # Kept loose on purpose, so a real contract is never skipped by mistake.
    is_contract = markers >= 3 and shall_count >= 3

    term_blanks = _term_blanks(full_text or "")
    blanks = len(term_blanks)

    if not is_contract:
        return ContractProfile(
            is_contract=False,
            contract_type="not_a_contract",
            contract_type_label=TYPE_LABELS["not_a_contract"],
            blank_fields=blanks,
        )

    scores = {kind: _distinct_cues(text, cues) for kind, cues in TYPE_CUES.items()}
    best = max(scores, key=lambda kind: len(scores[kind]))
    contract_type = best if len(scores[best]) >= 3 else "general"
    # A sale contract can mention "services" in passing; it needs clearly more sale cues
    if best == "sale_of_goods" and len(scores["sale_of_goods"]) <= len(scores["services"]):
        contract_type = "services" if len(scores["services"]) >= 3 else "general"

    return ContractProfile(
        is_contract=True,
        contract_type=contract_type,
        contract_type_label=TYPE_LABELS[contract_type],
        type_cues=scores.get(contract_type, []),
        is_template=blanks >= TEMPLATE_MIN_BLANKS,
        blank_fields=blanks,
        blank_examples=_blank_examples(full_text or "", term_blanks) if blanks >= TEMPLATE_MIN_BLANKS else [],
    )
