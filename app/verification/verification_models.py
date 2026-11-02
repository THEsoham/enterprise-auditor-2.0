from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    status: str
    verdict: str
    reasoning: str
    supporting_evidence: list[dict] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    # Which model actually produced the verdict, e.g. "gemini:gemini-3.6-flash"
    verifier_model: str = ""
    # True when Gemini was unavailable, so OpenAI (the Auditor's provider) gave the verdict
    verifier_is_fallback: bool = False
    # Result of the deterministic quote check run before the LLM verifier
    grounding: dict = Field(default_factory=dict)
