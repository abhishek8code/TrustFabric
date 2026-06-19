"""
IEEE-CIS Fraud Detection -> Behavioral Anomaly / Account-Takeover Detector
=============================================================================
Detector role in the Identity Trust Engine: Stage 3, "Behavioral Anomaly
Detection" sub-score, primarily covering Account Takeover + Behavioral
Anomalies + (partially) Suspicious Account Recovery risk mandates.

Dataset: https://www.kaggle.com/competitions/ieee-fraud-detection
Download train_transaction.csv and train_identity.csv and place them in
the DATA_DIR below (update the path to wherever you saved them).

Install deps:
    pip install pandas numpy lightgbm scikit-learn shap --break-system-packages
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve

# ---------------------------------------------------------------------------
# 0. CONFIG -- update this path to wherever you downloaded the CSVs
# ---------------------------------------------------------------------------
DATA_DIR = "./data/ieee-cis/"


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
def load_data(data_dir: str = DATA_DIR) -> pd.DataFrame:
    train_tx = pd.read_csv(data_dir + "train_transaction.csv")
    train_id = pd.read_csv(data_dir + "train_identity.csv")
    df = train_tx.merge(train_id, on="TransactionID", how="left")
    return df


# ---------------------------------------------------------------------------
# 2. FEATURE ENGINEERING
#    The UID trick below is the single highest-leverage feature in this
#    dataset: it approximately reconstructs "the same physical card/customer"
#    across multiple transactions, which is exactly the per-customer
#    baseline your Stage 2 feature store is meant to build.
# ---------------------------------------------------------------------------
def engineer_features(df: pd.DataFrame):
    df = df.sort_values("TransactionDT").reset_index(drop=True)

    # Amount-based signals
    df["TransactionAmt_log"] = np.log1p(df["TransactionAmt"])
    df["TransactionAmt_decimal"] = (
        (df["TransactionAmt"] - df["TransactionAmt"].astype(int)) * 1000
    ).astype(int)

    # Day index + normalized D1 (days since the card's first seen transaction)
    df["day"] = df["TransactionDT"] // (24 * 60 * 60)
    if "D1" in df.columns:
        df["D1n"] = df["D1"] - df["day"]

    # --- The "UID" pseudo-identity ---
    uid_cols = [c for c in ["card1", "card2", "addr1", "D1n"] if c in df.columns]
    df["uid"] = df[uid_cols].astype(str).agg("_".join, axis=1)
    uid_freq = df["uid"].value_counts().to_dict()
    df["uid_freq"] = df["uid"].map(uid_freq)  # how many txns from this "customer"

    # Frequency-encode high-cardinality categoricals
    freq_cols = ["card1", "card2", "card3", "card5", "addr1",
                 "P_emaildomain", "R_emaildomain"]
    for col in freq_cols:
        if col in df.columns:
            freq = df[col].value_counts(normalize=True).to_dict()
            df[col + "_freq"] = df[col].map(freq)

    # Email domain match signal (mismatch is a classic fraud signal)
    if "P_emaildomain" in df.columns and "R_emaildomain" in df.columns:
        df["email_domain_match"] = (
            df["P_emaildomain"] == df["R_emaildomain"]
        ).astype(int)

    cat_candidates = [
        "ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain",
        "DeviceType", "DeviceInfo",
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
    ]
    cat_cols = [c for c in cat_candidates if c in df.columns]
    for c in cat_cols:
        df[c] = df[c].astype("category")

    return df, cat_cols


# ---------------------------------------------------------------------------
# 3. TIME-BASED SPLIT
#    Never random-shuffle this dataset -- it is strictly time ordered and a
#    random split leaks future information into training.
# ---------------------------------------------------------------------------
def time_based_split(df: pd.DataFrame, val_frac: float = 0.2):
    cutoff = int(len(df) * (1 - val_frac))
    return df.iloc[:cutoff].copy(), df.iloc[cutoff:].copy()


# ---------------------------------------------------------------------------
# 4. TRAIN
# ---------------------------------------------------------------------------
def train_model(train_df, val_df, cat_cols, features):
    pos = train_df["isFraud"].sum()
    neg = len(train_df) - pos

    params = dict(
        objective="binary",
        metric="auc",
        boosting_type="gbdt",
        learning_rate=0.05,
        num_leaves=64,
        max_depth=-1,
        scale_pos_weight=neg / pos,   # handle class imbalance
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=1,
        min_data_in_leaf=50,
        verbosity=-1,
        seed=42,
    )

    train_set = lgb.Dataset(
        train_df[features], label=train_df["isFraud"], categorical_feature=cat_cols
    )
    val_set = lgb.Dataset(
        val_df[features], label=val_df["isFraud"],
        categorical_feature=cat_cols, reference=train_set,
    )

    model = lgb.train(
        params, train_set,
        num_boost_round=2000,
        valid_sets=[val_set],
        callbacks=[lgb.early_stopping(100), lgb.log_evaluation(100)],
    )
    return model


# ---------------------------------------------------------------------------
# 5. EVALUATE
#    AUC matches the original competition metric. PR-AUC and Recall@1%FPR
#    are more honest given how imbalanced fraud is, and Recall@1%FPR is a
#    good "business" number to quote in your pitch (e.g. "we catch X% of
#    fraud while only adding friction to 1% of genuine sessions").
# ---------------------------------------------------------------------------
def evaluate(model, val_df, features):
    preds = model.predict(val_df[features])
    auc = roc_auc_score(val_df["isFraud"], preds)
    pr_auc = average_precision_score(val_df["isFraud"], preds)

    fpr, tpr, _ = roc_curve(val_df["isFraud"], preds)
    idx = np.searchsorted(fpr, 0.01)
    recall_at_1pct_fpr = tpr[idx] if idx < len(tpr) else tpr[-1]

    print(f"ROC-AUC:           {auc:.4f}")
    print(f"PR-AUC:            {pr_auc:.4f}")
    print(f"Recall @ 1% FPR:   {recall_at_1pct_fpr:.4f}")
    return preds


# ---------------------------------------------------------------------------
# 6. EXPLAIN (SHAP) -- for your analyst-facing "why was this flagged" view
# ---------------------------------------------------------------------------
def explain(model, val_df, features, n=200):
    import shap
    explainer = shap.TreeExplainer(model)
    sample = val_df[features].sample(n, random_state=42)
    shap_values = explainer.shap_values(sample)
    return shap_values, sample


if __name__ == "__main__":
    print("Loading data...")
    df = load_data()

    print("Engineering features...")
    df, cat_cols = engineer_features(df)

    drop_cols = ["isFraud", "TransactionID", "TransactionDT", "uid"]
    features = [c for c in df.columns if c not in drop_cols]

    print("Splitting (time-based)...")
    train_df, val_df = time_based_split(df)

    print("Training LightGBM...")
    model = train_model(train_df, val_df, cat_cols, features)

    print("\nEvaluation:")
    val_preds = evaluate(model, val_df, features)

    # This is the per-transaction "behavioral anomaly sub-score" that feeds
    # into your Stage 4 meta risk-aggregation model.
    val_df["behavioral_anomaly_score"] = val_preds

    model.save_model("ieee_cis_lgb_model.txt")
    print("\nModel saved to ieee_cis_lgb_model.txt")
