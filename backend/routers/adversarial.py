from __future__ import annotations

from fastapi import APIRouter, Query

from backend.services.adversarial_service import AdversarialService
from backend.services.trust_engine import TrustEngine

router = APIRouter(prefix="/adversarial", tags=["Adversarial"])
adversarial_svc = AdversarialService(TrustEngine())


@router.get("/simulate")
async def simulate(attack: str = Query(default="SPOOFED_BIOMETRICS")):
    attack = attack.upper()
    if attack == "SPOOFED_BIOMETRICS":
        result = adversarial_svc.simulate_spoofed_biometrics()
        return {"result": result}
    if attack in {"BOILING_FROG", "BOILING_FROG_ATO"}:
        sessions = adversarial_svc.simulate_boiling_frog_ato()
        return {"result": {"attack": "BOILING_FROG", "sessions": sessions}}
    if attack == "GRAPH_EVASION":
        return {"result": adversarial_svc.simulate_graph_evasion()}
    return {"result": {"attack": attack, "message": "Unknown attack type"}}
