from typing import Literal, Optional
from pydantic import BaseModel, Field


BucketType = Literal["deal_breaker", "watch_out", "protection", "neutral"]


class FindingEvidence(BaseModel):
    chunk_id: str = ""
    page: Optional[int] = None
    quote: str = ""
    section: Optional[str] = None


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


class EnrichedFinding(BaseModel):
    finding_id: str = ""
    title: str
    category: str
    severity: str = "medium"
    bucket: BucketType
    claim: str
    plain_english: str = ""
    why_flagged: str = ""
    suggested_negotiation: str = ""
    clause_balance: Optional[ClauseBalance] = None
    evidence: list[dict] = Field(default_factory=list)
    confidence: float = 0.0
    verdict: str = "ACCEPTED"
    risk_score: Optional[dict] = None


class HealthScoreResult(BaseModel):
    health_score: float
    rating: str
    headline: str
    deal_breakers_count: int
    watch_out_count: int
    protections_count: int
    missing_protections_count: int
    deal_breakers: list[dict] = Field(default_factory=list)
    watch_out: list[dict] = Field(default_factory=list)
    protections: list[dict] = Field(default_factory=list)
    score_breakdown: dict = Field(default_factory=dict)