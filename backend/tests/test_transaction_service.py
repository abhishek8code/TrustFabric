from backend.models.transaction import TransactionRequest
from backend.services.transaction_service import TransactionService


def test_transaction_scoring_returns_probability_and_explanation():
    svc = TransactionService()
    req = TransactionRequest(
        transaction_id="tx-1",
        customer_id="cust_001",
        trust_token="stub",
        amount=25000,
        p_emaildomain="gmail.com",
        r_emaildomain="gmail.com",
    )
    fraud_probability, explanation = svc.score_transaction(req, trust_score=72.0)
    assert 0.0 <= fraud_probability <= 1.0
    assert explanation
