import json
import os
import re
import threading
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.verification.verification_models import VerificationResult


load_dotenv()

VALID_VERDICTS = {"ACCEPTED", "CORRECTED", "REJECTED", "UNSUPPORTED", "AMBIGUOUS"}


def parse_json_object(content: str | None) -> dict | None:
    """Parse a JSON object from an LLM reply, tolerating markdown fences and preamble."""
    if not content:
        return None

    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()

    try:
        parsed = json.loads(content)
    except Exception:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            return None

    return parsed if isinstance(parsed, dict) else None


class GeminiVerifier:
    """
    Independent Skeptic. Tries the configured Gemini models in order, then
    falls back to OpenAI. If every model fails, the finding is reported as
    UNVERIFIED instead of being silently accepted.
    """

    # A model that fails is skipped for this long, so one outage does not
    # slow down every remaining probe, but Gemini is retried later.
    COOLDOWN_SECONDS = 120
    _cooldown_until: dict[str, float] = {}
    _cooldown_lock = threading.Lock()

    def __init__(self, model: str | None = None):
        primary = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        fallbacks = os.getenv("GEMINI_FALLBACK_MODELS", "gemini-3.6-flash").split(",")
        self.models = list(dict.fromkeys(
            m.strip() for m in [primary, *fallbacks] if m.strip()
        ))
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        api_key = os.getenv("GEMINI_API_KEY")
        use_gemini = os.getenv("USE_GEMINI", "true").lower() == "true"
        self.client = None

        if api_key and use_gemini:
            try:
                self.client = genai.Client(
                    api_key=api_key,
                    # HttpOptions.timeout is in milliseconds
                    http_options=types.HttpOptions(
                        timeout=int(os.getenv("GEMINI_TIMEOUT_MS", "25000"))
                    ),
                )
            except Exception as e:
                print(f"[!] Gemini client could not be created ({e}). Using OpenAI Skeptic only.")

    def verify(
        self,
        finding: dict,
        evidence: list[dict]
    ) -> dict:

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

        prompt = f"""
You are the Skeptic in an enterprise contract auditing system.

An Auditor has produced the following finding:

AUDITOR FINDING:
{json.dumps(finding, indent=2)}

ORIGINAL CONTRACT EVIDENCE:
{evidence_text}

Your job is to verify whether the Auditor's finding is
actually supported by the supplied contract evidence.

RULES:

1. Use ONLY the supplied evidence.
2. Do not invent contractual language.
3. Check the Auditor's claim against the actual text.
4. Check whether the quoted evidence actually exists.
5. Check whether the page number is correct.
6. Check whether the chunk ID is correct.
7. Check whether the severity is proportionate to the text.
8. Identify contradictions or unsupported claims.
9. Do not perform a new independent audit.
10. Do not provide legal advice.
11. Return ONLY valid JSON.

Possible verdicts:

ACCEPTED     - claim, quotes and severity are all supported
CORRECTED    - mostly right, but something must be fixed (explain what)
AMBIGUOUS    - the evidence could be read either way
REJECTED     - the evidence contradicts the claim
UNSUPPORTED  - the evidence does not address the claim

Return exactly this structure:

{{
    "status": "verified",
    "verdict": "ACCEPTED",
    "reasoning": "explanation",
    "supporting_evidence": [
        {{
            "chunk_id": "chunk-XXXX",
            "page": 1,
            "quote": "exact supporting quote"
        }}
    ],
    "contradictions": [],
    "confidence": 0.0
}}
"""

        content, used_model = self._gemini_verify(prompt)
        if content is None:
            content, used_model = self._openai_verify(prompt)

        result = parse_json_object(content)
        if result is None:
            return self._unverified(
                "The Skeptic verifier was unavailable or returned an unreadable "
                "response, so this finding could not be independently verified.",
                used_model,
            )

        verdict = str(result.get("verdict", "AMBIGUOUS")).upper()
        if verdict not in VALID_VERDICTS:
            verdict = "AMBIGUOUS"

        try:
            confidence = float(result.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        return VerificationResult(
            status=str(result.get("status", "verified")),
            verdict=verdict,
            reasoning=str(result.get("reasoning", "")),
            supporting_evidence=[
                e for e in result.get("supporting_evidence") or [] if isinstance(e, dict)
            ],
            contradictions=[str(c) for c in result.get("contradictions") or []],
            confidence=max(0.0, min(confidence, 1.0)),
            verifier_model=used_model,
        ).model_dump()

    def _gemini_verify(self, prompt: str) -> tuple[str | None, str]:
        if not self.client:
            return None, ""

        for model in self.models:
            with self._cooldown_lock:
                if self._cooldown_until.get(model, 0.0) > time.time():
                    continue

            try:
                resp = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                    ),
                )
                if resp.text:
                    return resp.text, f"gemini:{model}"
            except Exception as e:
                with self._cooldown_lock:
                    self._cooldown_until[model] = time.time() + self.COOLDOWN_SECONDS
                print(f"[!] Gemini model {model} unavailable ({str(e)[:120]}). Trying next verifier.")

        return None, ""

    def _openai_verify(self, prompt: str) -> tuple[str | None, str]:
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an adversarial legal contract verifier and skeptic. "
                            "Analyze the claim against the provided evidence and return raw JSON strictly matching the requested structure."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                timeout=20.0,
            )
            return response.choices[0].message.content, f"openai:{self.openai_model}"
        except Exception as e:
            print(f"[!] OpenAI Skeptic fallback failed ({e}).")
            return None, ""

    @staticmethod
    def _unverified(reasoning: str, used_model: str = "") -> dict:
        return VerificationResult(
            status="unverified",
            verdict="UNVERIFIED",
            reasoning=reasoning,
            confidence=0.0,
            verifier_model=used_model or "none",
        ).model_dump()
