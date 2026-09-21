from typing import TypedDict


class DebateState(TypedDict, total=False):
    query: str

    finding: dict | None
    evidence: list[dict]

    verification: dict | None

    history: list[dict]

    round_number: int
    max_rounds: int

    final_status: str
    finished: bool