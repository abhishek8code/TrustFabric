from backend.models.token import TrustClaims
from backend.services.token_service import TokenService


def test_token_round_trip():
    svc = TokenService()
    now = 1_700_000_000
    claims = TrustClaims(
        sub="cust_001",
        channel="mobile",
        trust_score=72.5,
        trust_level="MEDIUM",
        session_id="session-1",
        iat=now,
        exp=now + 300,
    )
    token = svc.issue_token(claims)
    decoded = svc.verify_token(token)
    assert decoded.sub == claims.sub
    assert decoded.trust_level == claims.trust_level
