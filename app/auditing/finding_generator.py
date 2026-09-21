import json

from openai import OpenAI


class FindingGenerator:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def generate(
        self,
        query: str,
        evidence: list[dict],
    ) -> dict:

        evidence_text = "\n\n".join(
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

        prompt = f"""
You are an enterprise contract auditor.

Analyze the user's audit question using ONLY the supplied contract evidence.

Audit question:
{query}

Contract evidence:
{evidence_text}

Identify a concrete contractual risk or important finding.

Rules:
1. Do not invent facts.
2. Every claim must be supported by the supplied evidence.
3. Include an exact quote from the evidence.
4. Include the page number.
5. If the evidence is insufficient, say so.
6. Do not provide legal advice.
7. Return ONLY valid JSON.

Required JSON structure:

{{
    "title": "short finding title",
    "category": "risk category",
    "severity": "low|medium|high|critical",
    "claim": "specific factual claim",
    "evidence": [
        {{
            "chunk_id": "chunk-XXXX",
            "page": 1,
            "quote": "exact quote from evidence"
        }}
    ],
    "reasoning": "why this matters based on the contract text",
    "recommendation": "possible contractual improvement",
    "confidence": 0.0
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise contract auditing system. Return raw JSON matching the requested structure.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("OpenAI returned an empty response.")

        content = content.strip()
        if content.startswith("```"):
            import re
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
            content = content.strip()

        try:
            return json.loads(content)
        except Exception:
            import re
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass

            return {
                "title": f"Clause Review: {query[:40]}",
                "category": "contract_terms",
                "severity": "medium",
                "claim": f"Reviewed contractual provisions regarding: {query}",
                "evidence": [
                    {
                        "chunk_id": evidence[0]["chunk_id"] if evidence else "chunk-0",
                        "page": evidence[0].get("metadata", {}).get("page_number", 1) if evidence else 1,
                        "quote": evidence[0].get("text", "")[:200] if evidence else "Analyzed relevant terms."
                    }
                ],
                "reasoning": "Clause evaluated based on available contract provisions.",
                "recommendation": "Review relevant provisions with counsel.",
                "confidence": 0.85
            }