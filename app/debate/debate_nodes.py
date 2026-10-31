import copy

from app.auditing.auditor import Auditor
from app.verification.verifier import GeminiVerifier
from app.verification.grounding import ground_evidence
from app.verification.verification_models import VerificationResult


class DebateNodes:

    def __init__(self):
        self.auditor = Auditor()
        self.verifier = GeminiVerifier()

    def initial_audit(self, state: dict) -> dict:

        result = self.auditor.audit(
            query=state["query"],
            n_results=5,
        )

        state["finding"] = result.get("finding")
        state["evidence"] = result.get("evidence", [])

        return state

    def verify(self, state: dict) -> dict:

        finding = state.get("finding")

        if not finding:
            state["verification"] = VerificationResult(
                status="verified",
                verdict="UNSUPPORTED",
                reasoning="The Auditor did not generate a supported finding.",
                verifier_model="none",
            ).model_dump()

            return state

        # Deterministic check first: every quote must exist in the retrieved text.
        evidence = state.get("evidence", [])
        grounding = ground_evidence(finding, evidence)
        finding["evidence"] = grounding["grounded"]

        grounding_report = {
            "grounded_quotes": len(grounding["grounded"]),
            "ungrounded_quotes": [
                item.get("quote", "") for item in grounding["ungrounded"]
            ],
        }

        if not grounding["grounded"]:
            # No quote survived. Ask for a rebuttal if rounds remain; otherwise reject.
            final_round = state.get("round_number", 1) >= state.get("max_rounds", 3)
            state["verification"] = VerificationResult(
                status="verified",
                verdict="UNSUPPORTED" if final_round else "AMBIGUOUS",
                reasoning=(
                    "None of the quoted evidence could be found verbatim in the "
                    "retrieved contract text. Quotes must be copied exactly."
                ),
                contradictions=grounding_report["ungrounded_quotes"],
                verifier_model="grounding-check",
                grounding=grounding_report,
            ).model_dump()

            return state

        verification = self.verifier.verify(
            finding=finding,
            evidence=evidence,
        )
        verification["grounding"] = grounding_report

        state["verification"] = verification

        return state

    def rebuttal(self, state: dict) -> dict:

        revised_finding = self.auditor.generator.revise(
            query=state["query"],
            finding=state.get("finding") or {},
            verification=state.get("verification") or {},
            evidence=state.get("evidence", []),
        )

        # None means the Auditor conceded the finding cannot be supported
        state["finding"] = revised_finding

        state["round_number"] = (
            state.get("round_number", 1) + 1
        )

        return state

    def record_round(self, state: dict) -> dict:

        history = state.get("history", [])

        # Snapshot, so later rounds and scoring don't rewrite earlier rounds
        history.append(
            copy.deepcopy({
                "round": state.get("round_number", 1),
                "finding": state.get("finding"),
                "verification": state.get("verification"),
            })
        )

        state["history"] = history

        return state

    def finish(self, state: dict) -> dict:

        verification = state.get("verification") or {}

        state["final_status"] = verification.get(
            "verdict",
            "UNKNOWN",
        )

        state["finished"] = True

        return state
