from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    customer_id: str
    password_hash: str
    channel: str
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    keystroke_timings: Optional[list[float]] = None
    keystroke_hold_times: Optional[list[float]] = None


class StepUpRequest(BaseModel):
    session_id: str
    step_up_type: str
    otp_value: Optional[str] = None
    biometric_payload: Optional[dict] = None


class VerifyTokenRequest(BaseModel):
    token: str
    required_trust_level: str = "MEDIUM"
    action: Optional[str] = None
