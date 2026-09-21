from pydantic import BaseModel


class VerificationResult(BaseModel):
    status: str
    verdict: str
    reasoning: str
    supporting_evidence: list[dict]
    contradictions: list[str]
    confidence: float