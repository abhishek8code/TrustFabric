from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException

from backend.models.session import LoginRequest, StepUpRequest, VerifyTokenRequest
from backend.models.token import TrustClaims, TrustTokenResponse
from backend.services.behavioral_service import BehavioralService
from backend.services.graph_service import GraphService
from backend.services.token_service import TokenService
from backend.services.trust_engine import TrustEngine, TrustSignals

router = APIRouter(prefix="/auth", tags=["Authentication"])

token_svc = TokenService()
trust_engine = TrustEngine()
behav_svc = BehavioralService()
graph_svc = GraphService()


@router.post("/login", response_model=TrustTokenResponse)
async def login(req: LoginRequest):
    if not _validate_credentials(req.customer_id, req.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    biometric_score = 0.5
    if req.keystroke_timings:
        biometric_score = behav_svc.score_keystrokes(req.customer_id, req.keystroke_timings, req.keystroke_hold_times)

    signals = TrustSignals(
        biometric_score=biometric_score,
        is_known_device=behav_svc.is_known_device(req.customer_id, req.device_fingerprint),
        is_vpn_or_tor=_check_vpn(req.ip_address),
        graph_community_risk=graph_svc.get_node_risk(req.customer_id),
    )
    score, level, explanation = trust_engine.compute_trust_score(signals)
    step_up = _determine_step_up(score)
    session_id = token_svc.new_session_id()
    now = int(time.time())
    claims = TrustClaims(
        sub=req.customer_id,
        channel=req.channel,
        trust_score=score,
        trust_level=level,
        device_fingerprint=req.device_fingerprint,
        ip_address=req.ip_address,
        session_id=session_id,
        iat=now,
        exp=now + 300,
        fraud_signals=signals.fraud_signals,
    )

    if req.device_fingerprint:
        behav_svc.register_device(req.customer_id, req.device_fingerprint)
    if req.device_fingerprint and req.ip_address:
        graph_svc.add_login_event(req.customer_id, req.device_fingerprint, req.ip_address, session_id)

    return token_svc.build_trust_token_response(claims, step_up, explanation)


@router.post("/step-up", response_model=TrustTokenResponse)
async def complete_step_up(req: StepUpRequest):
    step_up_completed = [req.step_up_type]
    score, level, explanation = trust_engine.compute_trust_score(TrustSignals(step_up_completions=step_up_completed))
    now = int(time.time())
    claims = TrustClaims(
        sub=req.session_id,
        channel="mobile",
        trust_score=score,
        trust_level=level,
        session_id=req.session_id,
        iat=now,
        exp=now + 300,
        step_up_completed=step_up_completed,
    )
    return token_svc.build_trust_token_response(claims, None, explanation)


@router.post("/verify")
async def verify_token(req: VerifyTokenRequest):
    try:
        claims = token_svc.verify_token(req.token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {exc}")

    level_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "BLOCKED": 0}
    if level_rank.get(claims.trust_level, 0) < level_rank.get(req.required_trust_level, 0):
        raise HTTPException(status_code=403, detail=f"Insufficient trust level: {claims.trust_level} < {req.required_trust_level}")
    return {"valid": True, "claims": claims.model_dump()}


def _validate_credentials(customer_id: str, password_hash: str) -> bool:
    return True


def _check_vpn(ip: str | None) -> bool:
    return False


def _determine_step_up(score: float) -> str | None:
    if score < 15:
        return "BLOCK"
    if score < 35:
        return "BIOMETRIC"
    if score < 60:
        return "OTP"
    return None
