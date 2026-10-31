import re
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Obligation(BaseModel):
    obligation_id: str
    party: Literal["Provider", "Customer", "Mutual"]
    duty: str
    timeframe_label: str
    days: Optional[float] = None
    section: str
    page: int
    quote: str


class TimelineEvent(BaseModel):
    event_id: str
    period_label: str
    days: float
    party: str
    action: str
    section: str
    page: int
    quote: str


class ObligationsSummary(BaseModel):
    provider_obligations: list[Obligation] = Field(default_factory=list)
    customer_obligations: list[Obligation] = Field(default_factory=list)
    mutual_obligations: list[Obligation] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)


# Role words contracts commonly use for each side
PROVIDER_ROLES = ["provider", "vendor", "supplier", "licensor", "contractor", "seller", "consultant"]
CUSTOMER_ROLES = ["customer", "client", "buyer", "licensee", "purchaser", "subscriber"]
MUTUAL_ROLES = ["either party", "each party", "both parties", "the parties", "neither party", "parties"]

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "twelve": 12, "fourteen": 14, "fifteen": 15,
    "twenty": 20, "thirty": 30, "forty-five": 45, "sixty": 60, "ninety": 90,
}

UNIT_DAYS = {
    "hour": 1 / 24,
    "business day": 1.4,  # 5 business days ~ 7 calendar days
    "calendar day": 1.0,
    "day": 1.0,
    "week": 7.0,
    "month": 30.4,
    "year": 365.0,
}

_UNIT = r"(business days?|calendar days?|hours?|days?|weeks?|months?|years?)"
# "15 days", "thirty (30) days", "12-month", "20 business days"
DURATION_NUMERIC = re.compile(r"(?<![\d.])\(?(\d{1,4})\)?[\s-]*" + _UNIT + r"\b", re.IGNORECASE)
# "three months"
DURATION_WORDS = re.compile(
    r"\b(" + "|".join(NUMBER_WORDS) + r")[\s-]+" + _UNIT + r"\b", re.IGNORECASE
)

# Verbs that create a duty (obligations) and verbs that grant a right (timeline only)
DUTY_PATTERN = re.compile(
    r"\b(shall|must|will|agrees to|is required to|are required to|remains responsible)\b",
    re.IGNORECASE,
)
MODAL_PATTERN = re.compile(
    r"\b(shall|must|will|may|agrees to|is required to|are required to|remains responsible|is payable|are payable)\b",
    re.IGNORECASE,
)

CLAUSE_NUMBER = re.compile(r"^\d+(?:\.\d+)*\s+")
# Split after sentence punctuation (but not after a bare heading number like "2."),
# before numbered clauses like "10.3 Provider ...", and before headings like "9. LIMITATION"
SENTENCE_SPLIT = re.compile(
    r"(?<=[.;])(?<!\b\d\.)(?<!\b\d\d\.)\s+(?=[A-Z(])"
    r"|\s+(?=\d{1,2}\.\d{1,2}\s+[A-Z])"
    r"|\s+(?=\d{1,2}\.\s+[A-Z][A-Z &\-]{2,}\b)"
)


def _contains_role(text: str, roles: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(r)}\b", text) for r in roles)


def classify_party(
    subject: str,
    provider_roles: list[str] = PROVIDER_ROLES,
    customer_roles: list[str] = CUSTOMER_ROLES,
) -> Optional[str]:
    """Map the subject of a sentence to Provider / Customer / Mutual, or None."""
    subject = subject.lower()
    if _contains_role(subject, MUTUAL_ROLES):
        return "Mutual"

    provider = _contains_role(subject, provider_roles)
    customer = _contains_role(subject, customer_roles)
    if provider and customer:
        # Whichever role appears last is closest to the verb, so it is the subject
        last_provider = max(subject.rfind(r) for r in provider_roles)
        last_customer = max(subject.rfind(r) for r in customer_roles)
        return "Provider" if last_provider > last_customer else "Customer"
    if provider:
        return "Provider"
    if customer:
        return "Customer"
    if re.search(r"\bparty\b", subject):
        return "Mutual"
    return None


def find_durations(sentence: str) -> list[tuple[str, float]]:
    """All time periods in a sentence as (label, days)."""
    found = []
    for match in DURATION_NUMERIC.finditer(sentence):
        number = float(match.group(1))
        found.append((match.start(), match.group(0).strip("() "), number, match.group(2)))
    for match in DURATION_WORDS.finditer(sentence):
        number = float(NUMBER_WORDS[match.group(1).lower()])
        found.append((match.start(), match.group(0), number, match.group(2)))

    durations = []
    for _, label, number, unit in sorted(found):
        unit_key = unit.lower().rstrip("s")
        days = number * UNIT_DAYS.get(unit_key, 1.0)
        durations.append((label, round(days, 2)))
    return durations


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = []
    for sentence in SENTENCE_SPLIT.split(text):
        # Drop a leading section heading such as "15. FORCE MAJEURE Neither Party ..."
        sentence = re.sub(r"^\d{1,2}\.\s+[A-Z][A-Z &\-]{2,}(?=\s[A-Z][a-z])", "", sentence.strip())
        sentence = CLAUSE_NUMBER.sub("", sentence.strip())
        if len(sentence) >= 20:
            sentences.append(sentence)
    return sentences


class ObligationExtractor:
    """
    Extracts party-specific obligations and constructs a chronological
    timeline map of deadlines, notice periods, and operational milestones,
    directly from the contract text. Every item keeps its verbatim quote,
    section, and page.
    """

    MAX_DUTY_CHARS = 220

    def extract(
        self,
        chunks_or_text: list[dict] | str,
        parties: Optional[dict[str, str]] = None,
    ) -> ObligationsSummary:
        """Extract obligations and return summary with structured timeline."""
        if isinstance(chunks_or_text, str):
            chunks = [{"text": chunks_or_text, "page_number": 1, "section": ""}]
        else:
            chunks = chunks_or_text or []

        provider_roles, customer_roles = self._roles_for(parties)

        prov_obls: list[Obligation] = []
        cust_obls: list[Obligation] = []
        mut_obls: list[Obligation] = []
        timeline: list[TimelineEvent] = []
        seen: set[str] = set()

        for chunk in chunks:
            metadata = chunk.get("metadata") or {}
            page = int(chunk.get("page_number") or metadata.get("page_number") or 1)
            section = chunk.get("section") or metadata.get("section") or ""

            for sentence in split_sentences(chunk.get("text", "")):
                key = sentence.lower()
                if key in seen or " means " in key:
                    continue
                seen.add(key)

                modal = MODAL_PATTERN.search(sentence)
                if not modal:
                    continue

                # Only the grammatical subject decides who owes a duty; a role
                # mentioned elsewhere in the sentence is enough for the timeline.
                subject = sentence[: modal.start()][-80:]
                party = classify_party(subject, provider_roles, customer_roles)
                timeline_party = party or classify_party(sentence, provider_roles, customer_roles)

                durations = find_durations(sentence)
                duty_text = self._trim(sentence)

                if party and DUTY_PATTERN.search(sentence):
                    label, days = durations[0] if durations else ("Ongoing", None)
                    obligation = Obligation(
                        obligation_id=f"obl-{len(prov_obls) + len(cust_obls) + len(mut_obls) + 1:03d}",
                        party=party,
                        duty=duty_text,
                        timeframe_label=label,
                        days=days,
                        section=section,
                        page=page,
                        quote=sentence,
                    )
                    {"Provider": prov_obls, "Customer": cust_obls}.get(party, mut_obls).append(obligation)

                for label, days in durations:
                    timeline.append(TimelineEvent(
                        event_id=f"time-{len(timeline) + 1:03d}",
                        period_label=label,
                        days=days,
                        party=timeline_party or "General",
                        action=duty_text,
                        section=section,
                        page=page,
                        quote=sentence,
                    ))

        timeline.sort(key=lambda t: t.days)

        return ObligationsSummary(
            provider_obligations=prov_obls,
            customer_obligations=cust_obls,
            mutual_obligations=mut_obls,
            timeline=timeline,
        )

    @staticmethod
    def _roles_for(parties: Optional[dict[str, str]]) -> tuple[list[str], list[str]]:
        """Add the contract's actual party names (e.g. 'Northstar') to the role words."""
        provider_roles = list(PROVIDER_ROLES)
        customer_roles = list(CUSTOMER_ROLES)
        parties = parties or {}

        for key, roles in (("provider", provider_roles), ("customer", customer_roles)):
            name = str(parties.get(key) or "").strip().lower()
            first_word = name.split()[0] if name else ""
            if first_word and first_word not in (PROVIDER_ROLES + CUSTOMER_ROLES) and len(first_word) > 2:
                roles.append(first_word)

        return provider_roles, customer_roles

    def _trim(self, sentence: str) -> str:
        if len(sentence) <= self.MAX_DUTY_CHARS:
            return sentence
        return sentence[: self.MAX_DUTY_CHARS].rsplit(" ", 1)[0] + "…"
