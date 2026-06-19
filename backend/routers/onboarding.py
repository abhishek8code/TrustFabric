from __future__ import annotations

from fastapi import APIRouter

from backend.models.onboarding import IdentityRiskScore, OnboardingApplication
from backend.services.identity_service import IdentityService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])
identity_svc = IdentityService()


@router.post("/check", response_model=IdentityRiskScore)
async def check_identity(app: OnboardingApplication):
    result = identity_svc.check_identity_recycling(app.model_dump())
    
    # If identity is suspicious, trigger a dynamic SOC alert
    if result["risk_level"] != "CLEAR":
        from backend.routers.admin import add_admin_alert
        severity = "high" if result["risk_level"] == "BLOCK" else "medium"
        add_admin_alert(
            severity=severity,
            message=f"KYC recycled identity alert ({result['risk_level']}): {app.full_name} matches {result['closest_match_id'] or 'existing'} (similarity {result['max_similarity']:.2f})"
        )
    else:
        # Save clear applications to build history baseline
        identity_svc.enroll_application(app.application_id, app.model_dump())

    return IdentityRiskScore(
        application_id=app.application_id,
        max_similarity_score=result["max_similarity"],
        closest_match_id=result["closest_match_id"],
        risk_level=result["risk_level"],
        explanation=result["explanation"],
    )
