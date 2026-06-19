from typing import Optional

from pydantic import BaseModel


class TransactionRequest(BaseModel):
    transaction_id: str
    customer_id: str
    trust_token: str
    amount: float
    product_cd: Optional[str] = None
    card1: Optional[int] = None
    card2: Optional[int] = None
    card4: Optional[str] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    dist1: Optional[float] = None
    p_emaildomain: Optional[str] = None
    r_emaildomain: Optional[str] = None
    d1: Optional[float] = None
    d2: Optional[float] = None
    c1: Optional[float] = None
    c2: Optional[float] = None
    v_columns: Optional[dict[str, float]] = None


class TransactionScore(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_flagged: bool
    trust_degradation: float
    shap_explanation: list[dict]
    action: str
