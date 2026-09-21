def route_after_verification(state: dict) -> str:
    verification = state.get("verification") or {}

    verdict = str(
        verification.get("verdict", "AMBIGUOUS")
    ).upper()

    round_number = state.get("round_number", 1)
    max_rounds = state.get("max_rounds", 3)

    if verdict in {
        "ACCEPTED",
        "REJECTED",
        "UNSUPPORTED",
    }:
        return "finish"

    if round_number >= max_rounds:
        return "finish"

    if verdict in {
        "CORRECTED",
        "AMBIGUOUS",
    }:
        return "rebuttal"

    return "finish"