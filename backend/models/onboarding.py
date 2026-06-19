from typing import Optional

from pydantic import BaseModel


class OnboardingApplication(BaseModel):
    application_id: str
    full_name: str
    aadhaar_hash: str
    pan_hash: str
    dob: str
    mobile_last4: str
    pincode: str
    email_domain: str


class IdentityRiskScore(BaseModel):
    application_id: str
    max_similarity_score: float
    closest_match_id: Optional[str]
    risk_level: str
    explanation: str
