from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

from backend.config import settings
from backend.models.transaction import TransactionRequest
from backend.ml.lgbm_model import LGBMFraudModel
from backend.utils.feature_engineering import engineer_features, CATEGORICAL_COLS


class TransactionService:
    def __init__(self):
        self._model_path = Path(settings.LGBM_MODEL_PATH)
        self._model: LGBMFraudModel | None = None
        self._load_model()

    def _load_model(self):
        if self._model_path.exists():
            try:
                self._model = LGBMFraudModel(str(self._model_path))
                print("[OK] Loaded LGBMFraudModel successfully.")
            except Exception as e:
                print(f"[WARN] Failed to load LGBMFraudModel: {e}")
                self._model = None

    def score_transaction(self, request: TransactionRequest, trust_score: float = 50.0) -> tuple[float, list[dict]]:
        if self._model is None:
            self._load_model()

        # Build raw dict for pandas DataFrame
        raw_data = {
            "TransactionID": [request.transaction_id],
            "TransactionAmt": [request.amount],
            "ProductCD": [request.product_cd or "W"],
            "card1": [request.card1 or 1000],
            "card2": [request.card2 or 100.0],
            "card4": [request.card4 or "visa"],
            "card6": [request.card6 or "debit"],
            "addr1": [request.addr1 or 299.0],
            "addr2": [request.addr2 or 87.0],
            "dist1": [request.dist1 or 0.0],
            "P_emaildomain": [request.p_emaildomain or "gmail.com"],
            "R_emaildomain": [request.r_emaildomain or "gmail.com"],
            "D1": [request.d1 if request.d1 is not None else 0.0],
            "D2": [request.d2 if request.d2 is not None else 0.0],
            "TransactionDT": [0.0]
        }

        # Add V columns if provided
        if request.v_columns:
            for k, v in request.v_columns.items():
                raw_data[k] = [v]

        df = pd.DataFrame(raw_data)
        
        # Engineer features
        df_engineered = engineer_features(df)

        if self._model and self._model.model is not None:
            # Align features with training columns
            for col in self._model.feature_names:
                if col not in df_engineered.columns:
                    if col in CATEGORICAL_COLS:
                        df_engineered[col] = pd.Series([np.nan], dtype="category")
                    else:
                        df_engineered[col] = 0.0
            
            # Predict
            try:
                fraud_prob = float(self._model.predict_proba(df_engineered)[0])
                explanation = self._model.explain(df_engineered)
                return round(fraud_prob, 4), explanation
            except Exception as e:
                print(f"[WARN] Inference failed: {e}. Falling back to default scoring.")

        # Robust default fallback rule if model is not loaded/trained
        amount_score = min(1.0, request.amount / 100000.0)
        domain_penalty = 0.2 if request.p_emaildomain != request.r_emaildomain else 0.0
        fraud_probability = max(0.0, min(1.0, 0.15 + 0.65 * amount_score + domain_penalty + (50.0 - trust_score) / 200.0))
        explanation = [
            {"feature": "amount", "value": request.amount, "shap_impact": round(amount_score, 4)},
            {"feature": "email_domain_match", "value": float(request.p_emaildomain == request.r_emaildomain), "shap_impact": round(-domain_penalty, 4)},
        ]
        return round(fraud_probability, 4), explanation
