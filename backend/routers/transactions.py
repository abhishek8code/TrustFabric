from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.transaction import TransactionRequest, TransactionScore
from backend.services.graph_service import GraphService
from backend.services.token_service import TokenService
from backend.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

token_svc = TokenService()
transaction_svc = TransactionService()
graph_svc = GraphService()


@router.post("/score", response_model=TransactionScore)
async def score_transaction(req: TransactionRequest):
    try:
        claims = token_svc.verify_token(req.trust_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid trust token: {exc}")

    fraud_probability, explanation = transaction_svc.score_transaction(req, claims.trust_score)
    graph_svc.add_transaction_event(req.customer_id, f"beneficiary:{req.customer_id}", req.amount, req.transaction_id)

    if fraud_probability >= 0.70:
        action = "BLOCK"
    elif fraud_probability >= 0.40:
        action = "STEP_UP"
    else:
        action = "ALLOW"

    is_flagged = action != "ALLOW"
    trust_degradation = round(min(20.0, fraud_probability * 20.0), 2)
    
    # If transaction is suspicious, trigger a dynamic SOC alert
    if is_flagged:
        from backend.routers.admin import add_admin_alert
        severity = "high" if action == "BLOCK" else "medium"
        add_admin_alert(
            severity=severity,
            message=f"Suspicious txn {req.transaction_id} from {req.customer_id}: INR {req.amount:,.2f} flagged as {action} (Score: {fraud_probability:.1%})"
        )

    return TransactionScore(
        transaction_id=req.transaction_id,
        fraud_probability=fraud_probability,
        is_flagged=is_flagged,
        trust_degradation=trust_degradation,
        shap_explanation=explanation,
        action=action,
    )
