from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from backend.services.token_service import TokenService

router = APIRouter(prefix="/trust-passport", tags=["Trust Passport"])
token_svc = TokenService()


@router.get("/me")
async def me(x_trust_token: str | None = Header(default=None, alias="X-Trust-Token")):
    if not x_trust_token:
        # Fallback to default mock claims for initial demo display when not logged in
        return {
            "trust_score": 72.0,
            "trust_level": "MEDIUM",
            "explanation": [
                "Typing pattern verified ✓",
                "Known device used ✓",
                "No recent high-risk transfer flagged.",
            ],
            "recent_events": [
                {"description": "Verified login from registered device", "time": "Today"},
                {"description": "Password reset on hold: trust threshold not met", "time": "Yesterday"},
            ],
        }

    try:
        claims = token_svc.verify_token(x_trust_token)
        
        # Format dynamic events
        device_str = f"Device fingerprint: {claims.device_fingerprint[:12]}..." if claims.device_fingerprint else "Unidentified device footprint"
        ip_str = f"IP address logged: {claims.ip_address}" if claims.ip_address else "No IP data"
        
        # Build explanation list based on score & channel
        explanation = []
        if claims.trust_score >= 75:
            explanation.append("Secure channel baseline verified ✓")
            explanation.append("Session activity indicates low risk profile ✓")
        elif claims.trust_score >= 50:
            explanation.append("Session profile verified under medium-risk thresholds ✓")
        else:
            explanation.append("⚠ High risk factors flagged in this session")

        if claims.fraud_signals:
            explanation.extend(claims.fraud_signals)
        else:
            explanation.append("No active fraud patterns detected ✓")

        return {
            "trust_score": claims.trust_score,
            "trust_level": claims.trust_level,
            "explanation": explanation,
            "recent_events": [
                {"description": f"Verified session established via {claims.channel}", "time": "Just now"},
                {"description": device_str, "time": "Just now"},
                {"description": ip_str, "time": "Just now"},
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {exc}")
