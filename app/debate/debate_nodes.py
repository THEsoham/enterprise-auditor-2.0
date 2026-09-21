from app.auditing.auditor import Auditor
from app.verification.verifier import GeminiVerifier
import os
from dotenv import load_dotenv

load_dotenv()

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
            state["verification"] = {
                "status": "verified",
                "verdict": "UNSUPPORTED",
                "reasoning": (
                    "The Auditor did not generate "
                    "a supported finding."
                ),
                "supporting_evidence": [],
                "contradictions": [],
                "confidence": 0.0,
            }

            return state

        verification = self.verifier.verify(
            finding=finding,
            evidence=state.get("evidence", []),
        )

        state["verification"] = verification

        return state

    def rebuttal(self, state: dict) -> dict:

        finding = state.get("finding") or {}
        verification = state.get("verification") or {}

        evidence = state.get("evidence", [])

        evidence_text = "\n\n".join(
            [
                (
                    f"CHUNK ID: {item['chunk_id']}\n"
                    f"PAGE: {item['metadata'].get('page_number')}\n"
                    f"SECTION: {item['metadata'].get('section')}\n"
                    f"TEXT:\n{item['text']}"
                )
                for item in evidence
            ]
        )

        query = f"""
Re-evaluate the previous audit finding.

ORIGINAL AUDIT QUESTION:
{state["query"]}

PREVIOUS FINDING:
{finding}

GEMINI SKEPTIC REVIEW:
{verification}

ORIGINAL CONTRACT EVIDENCE:
{evidence_text}

Your task is to produce a revised finding.

Rules:

1. Address Gemini's objections explicitly.
2. Use ONLY the supplied contract evidence.
3. Do not invent facts.
4. Preserve valid parts of the previous finding.
5. Correct unsupported claims.
6. Every factual claim must have evidence.
7. Every evidence item must contain an exact quote.
8. Include the correct chunk ID and page.
9. If the original finding cannot be supported, return
   status "unsupported".
10. Return ONLY valid JSON.

Return:

{{
    "status": "supported|unsupported",
    "title": "short finding title",
    "category": "risk category",
    "severity": "low|medium|high|critical",
    "claim": "specific factual claim",
    "evidence": [
        {{
            "chunk_id": "chunk-XXXX",
            "page": 1,
            "quote": "exact quote"
        }}
    ],
    "reasoning": "reasoning based only on evidence",
    "recommendation": "possible contractual improvement",
    "confidence": 0.0
}}
"""

        from openai import OpenAI
        import json
        import re

        client = OpenAI()

        response = client.chat.completions.create(
            model=os.getenv(
                "OPENAI_MODEL",
                 "gpt-4o-mini"
                ),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the Auditor in a "
                        "multi-agent contract audit debate. "
                        "Return raw JSON matching the requested structure."
                    ),
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "OpenAI returned an empty rebuttal."
            )

        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            content = content.strip()

        try:
            revised_finding = json.loads(content)
        except Exception:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                try:
                    revised_finding = json.loads(match.group(0))
                except Exception:
                    revised_finding = finding
            else:
                revised_finding = finding

        state["finding"] = revised_finding

        state["round_number"] = (
            state.get("round_number", 1) + 1
        )

        return state

    def record_round(self, state: dict) -> dict:

        history = state.get("history", [])

        history.append(
            {
                "round": state.get("round_number", 1),
                "finding": state.get("finding"),
                "verification": state.get("verification"),
            }
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