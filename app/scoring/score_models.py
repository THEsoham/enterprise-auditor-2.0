from typing import Literal
from pydantic import BaseModel


BucketType = Literal["deal_breaker", "watch_out", "protection", "neutral"]


class ClauseBalance(BaseModel):
    is_asymmetric: bool = False
    provider_terms: str = ""
    customer_terms: str = ""
    asymmetry_summary: str = ""


class RiskScore(BaseModel):
    severity_score: float
    confidence_score: float
    verification_score: float
    evidence_score: float
    final_score: float
    risk_level: str
    bucket: BucketType = "watch_out"