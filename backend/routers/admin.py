from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])

# Global in-memory log of alerts to make the dashboard live and interactive
ACTIVE_ALERTS = [
    {"id": "ALERT-001", "severity": "high", "message": "Shared device pattern detected: CUST_MULE_001 using DEV_MULE_SHARED"},
    {"id": "ALERT-002", "severity": "medium", "message": "Identity recycling risk detected at KYC onboarding: Priya Sharma2 matches Priya Sharma (similarity 0.88)"},
]


@router.get("/alerts")
async def alerts():
    return {"alerts": ACTIVE_ALERTS}


def add_admin_alert(severity: str, message: str):
    alert_id = f"ALERT-{len(ACTIVE_ALERTS) + 1:03d}"
    ACTIVE_ALERTS.insert(0, {"id": alert_id, "severity": severity, "message": message})
