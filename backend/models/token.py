from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TrustClaims(BaseModel):
    sub: str
    channel: str
    trust_score: float
    trust_level: Literal["HIGH", "MEDIUM", "LOW", "BLOCKED"]
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: str
    iat: int
    exp: int
    issuer: str = "trustfabric.bob.in"
    step_up_completed: list[str] = Field(default_factory=list)
    fraud_signals: list[str] = Field(default_factory=list)


class TrustTokenResponse(BaseModel):
    token: str
    trust_level: str
    trust_score: float
    step_up_required: Optional[str] = None
    expires_at: datetime
    explanation: list[str]
    session_id: Optional[str] = None
