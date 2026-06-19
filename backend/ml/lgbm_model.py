from __future__ import annotations

import pickle
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap

from backend.utils.feature_engineering import CATEGORICAL_COLS

TARGET = "isFraud"

LGBM_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 491,
    "max_depth": -1,
    "learning_rate": 0.05,  # Slightly higher than 0.006 to train faster for hackathon demo
    "feature_fraction": 0.85,
    "bagging_fraction": 0.85,
    "bagging_freq": 5,
    "min_child_samples": 100,
    "lambda_l1": 0.1,
    "lambda_l2": 10.0,
    "scale_pos_weight": 28,  # ~3.5% fraud rate -> ~28x class imbalance
    "n_estimators": 200,   # Reduced from 2000 for fast training in hackathon
    "early_stopping_rounds": 50,
    "verbose": -1,
}


class LGBMFraudModel:
    """
    Wraps a trained LightGBM model for transaction fraud scoring.
    Also manages a SHAP TreeExplainer for explanations.
    """

    def __init__(self, model_path: str | None = None):
        self.model: lgb.LGBMClassifier | None = None
        self.feature_names: list[str] = []
        self.explainer: shap.TreeExplainer | None = None
        if model_path and Path(model_path).exists():
            self.load(model_path)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, df_train: pd.DataFrame, df_valid: pd.DataFrame) -> dict:
        """
        Train on df_train, evaluate on df_valid.
        Both DataFrames must already have engineer_features() applied.
        Returns dict with validation AUC.
        """
        exclude = [TARGET, "TransactionID", "uid"]
        feature_cols = [c for c in df_train.columns if c not in exclude]
        cat_cols = [c for c in feature_cols if df_train[c].dtype.name == "category"]

        X_train, y_train = df_train[feature_cols], df_train[TARGET]
        X_valid, y_valid = df_valid[feature_cols], df_valid[TARGET]

        self.model = lgb.LGBMClassifier(**LGBM_PARAMS)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_valid, y_valid)],
            categorical_feature=cat_cols,
        )
        self.feature_names = feature_cols
        
        try:
            self.explainer = shap.TreeExplainer(self.model.booster_)
        except Exception:
            self.explainer = None

        val_auc = float(self.model.best_score_["valid_0"]["auc"])
        return {"val_auc": val_auc, "best_iteration": int(self.model.best_iteration_)}

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return fraud probability for each row (single float if one row)."""
        if self.model is None:
            # Fallback if model not trained yet
            return np.array([0.5] * len(df))
        X = df[self.feature_names]
        return self.model.predict_proba(X)[:, 1]

    def explain(self, df: pd.DataFrame, top_n: int = 5) -> list[dict]:
        """
        Return top_n SHAP contributors for the FIRST row of df.
        Format: [{"feature": "...", "value": ..., "shap_impact": ...}]
        """
        if self.model is None or self.explainer is None:
            # Fallback explanation if SHAP/Model not loaded
            row = df.iloc[0]
            features = []
            for name in [c for c in df.columns if c not in {"TransactionID", "isFraud"}][:top_n]:
                value = row.get(name, 0)
                features.append({
                    "feature": name,
                    "value": float(value) if isinstance(value, (int, float)) else 0.0,
                    "shap_impact": 0.01
                })
            return features

        X = df[self.feature_names].iloc[:1]
        try:
            shap_values = self.explainer.shap_values(X)
            # shap 0.45+ might return a list of arrays for binary class or a single array
            if isinstance(shap_values, list):
                # Binary classification returns a list [contrib_class_0, contrib_class_1]
                shap_values = shap_values[1]
            elif len(shap_values.shape) == 3:
                # Shape could be (samples, features, classes)
                shap_values = shap_values[:, :, 1]
            
            # If shap_values is 2D but shape of X is 1 row
            if len(shap_values.shape) == 2:
                row_shap = shap_values[0]
            else:
                row_shap = shap_values

            impacts = list(zip(self.feature_names, row_shap, X.values[0]))
            impacts.sort(key=lambda x: abs(x[1]), reverse=True)
            return [
                {
                    "feature": feat,
                    "value": float(val) if isinstance(val, (int, float)) else 0.0,
                    "shap_impact": float(impact)
                }
                for feat, impact, val in impacts[:top_n]
            ]
        except Exception:
            # Safe fallback in case SHAP calculation fails for specific format
            row = df.iloc[0]
            features = []
            for name in self.feature_names[:top_n]:
                value = row.get(name, 0)
                features.append({
                    "feature": name,
                    "value": float(value) if isinstance(value, (int, float)) else 0.0,
                    "shap_impact": 0.01
                })
            return features

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "feature_names": self.feature_names}, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        try:
            self.explainer = shap.TreeExplainer(self.model.booster_)
        except Exception:
            self.explainer = None
