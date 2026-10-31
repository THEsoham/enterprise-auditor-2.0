import json
import os

from openai import OpenAI

from app.verification.verifier import parse_json_object


FINDING_SCHEMA = """
{
    "status": "supported|unsupported",
    "title": "short finding title",
    "category": "risk category",
    "finding_type": "risk|protection",
    "severity": "low|medium|high|critical",
    "claim": "specific factual claim",
    "evidence": [
        {
            "chunk_id": "chunk-XXXX",
            "page": 1,
            "section": "section heading",
            "quote": "exact quote copied character-for-character from the evidence"
        }
    ],
    "reasoning": "why this matters based on the contract text",
    "recommendation": "possible contractual improvement",
    "plain_english": "one or two sentences a non-lawyer understands",
    "why_flagged": "short explanation of why a reviewer should care",
    "suggested_negotiation": "concrete redline wording the reader could propose",
    "clause_balance": {
        "is_asymmetric": false,
        "provider_terms": "what the provider-side party gets under this clause, or empty",
        "customer_terms": "what the customer-side party gets under this clause, or empty",
        "asymmetry_summary": "one sentence on the imbalance, or empty"
    },
    "confidence": 0.0
}
"""

FINDING_RULES = """
Perspective: you review the contract on behalf of the CUSTOMER (the party buying
the services). "Risk" and "protection" are always judged from the Customer's side.

Severity rubric (from the Customer's point of view):
- critical: could be fatal to the deal. Examples: the other party can exit at will
  on very short notice while the Customer is locked in; liability capped so low
  that serious harm is effectively unrecoverable; broad one-sided rights over the
  Customer's data or money.
- high: significant one-sided exposure the Customer should negotiate before signing.
- medium: common but noteworthy terms (auto-renewal windows, retention periods,
  restricted audit rights, publicity rights).
- low: minor or standard terms.

finding_type:
- "protection" only when the clause, on balance, protects the Customer
  (e.g. the Provider is responsible for its subcontractors, mutual confidentiality,
  the Customer keeps ownership of its data).
- "risk" when the clause grants the other party a right or permission that can
  hurt the Customer (e.g. "Provider may retain...", "Provider may terminate...").

clause_balance.is_asymmetric is true only when the two parties get materially
different rights or obligations under the SAME clause.

Rules:
1. Do not invent facts.
2. Every claim must be supported by the supplied evidence.
3. Every evidence item must contain an EXACT quote copied from the evidence text.
   Quotes are checked automatically; paraphrased quotes are discarded.
4. Include the chunk ID and page number the quote came from.
5. If the evidence is insufficient, return status "unsupported".
6. Do not provide legal advice.
7. Return ONLY valid JSON.
"""


def format_evidence(evidence: list[dict]) -> str:
    return "\n\n".join(
        [
            (
                f"Chunk ID: {item['chunk_id']}\n"
                f"Page: {item['metadata'].get('page_number')}\n"
                f"Section: {item['metadata'].get('section')}\n"
                f"Text:\n{item['text']}"
            )
            for item in evidence
        ]
    )


class FindingGenerator:
    def __init__(self, model: str | None = None):
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(
        self,
        query: str,
        evidence: list[dict],
    ) -> dict | None:
        """Returns a finding, or None when the evidence does not support one."""

        prompt = f"""
You are an enterprise contract auditor.

Analyze the user's audit question using ONLY the supplied contract evidence.

Audit question:
{query}

Contract evidence:
{format_evidence(evidence)}

Identify a concrete contractual risk, protection, or important finding.
{FINDING_RULES}
Required JSON structure:
{FINDING_SCHEMA}
"""

        return self._complete(
            system="You are a precise contract auditing system. Return raw JSON matching the requested structure.",
            prompt=prompt,
        )

    def revise(
        self,
        query: str,
        finding: dict,
        verification: dict,
        evidence: list[dict],
    ) -> dict | None:
        """Rebuttal round: rewrite the finding to address the Skeptic's objections."""

        prompt = f"""
Re-evaluate the previous audit finding.

ORIGINAL AUDIT QUESTION:
{query}

PREVIOUS FINDING:
{json.dumps(finding, indent=2)}

SKEPTIC REVIEW:
{json.dumps(verification, indent=2)}

ORIGINAL CONTRACT EVIDENCE:
{format_evidence(evidence)}

Produce a revised finding. Address the Skeptic's objections explicitly,
keep the valid parts of the previous finding, and correct unsupported claims.
If the original finding cannot be supported, return status "unsupported".
{FINDING_RULES}
Required JSON structure:
{FINDING_SCHEMA}
"""

        return self._complete(
            system="You are the Auditor in a multi-agent contract audit debate. Return raw JSON matching the requested structure.",
            prompt=prompt,
        )

    def _complete(self, system: str, prompt: str) -> dict | None:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
            timeout=20.0,
        )

        finding = parse_json_object(response.choices[0].message.content)

        # An unreadable reply or an explicit "unsupported" is not a finding;
        # never substitute a made-up one.
        if not finding or str(finding.get("status", "")).lower() == "unsupported":
            return None

        return finding
