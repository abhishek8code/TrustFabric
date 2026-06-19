import pandas as pd
from pathlib import Path
import sys

# Add root folder to sys.path so we can import from backend
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.utils.feature_engineering import engineer_features, time_based_split
from backend.ml.lgbm_model import LGBMFraudModel

def main():
    # Detect CSV location
    root_dir = Path(__file__).resolve().parents[1]
    
    tx_path = root_dir / "train_transaction.csv"
    id_path = root_dir / "train_identity.csv"
    
    if not tx_path.exists():
        # Fallback to data folder
        tx_path = root_dir / "data" / "raw" / "ieee_cis" / "train_transaction.csv"
        id_path = root_dir / "data" / "raw" / "ieee_cis" / "train_identity.csv"

    if not tx_path.exists():
        print(f"ERROR: train_transaction.csv not found at {tx_path} or in root.")
        print("Please place train_transaction.csv and train_identity.csv in the root or data/raw/ieee_cis/.")
        sys.exit(1)

    print(f"Loading IEEE-CIS data from {tx_path}...")
    tx = pd.read_csv(tx_path)
    id_ = pd.read_csv(id_path) if id_path.exists() else pd.DataFrame(columns=["TransactionID"])
    df = tx.merge(id_, on="TransactionID", how="left")

    # Fast sampling for hackathon demo
    # We sample 5% of the data to speed up feature engineering and LightGBM training
    sample_frac = 0.05
    print(f"Sampling {sample_frac:.0%} of the data for fast training...")
    df = df.sample(frac=sample_frac, random_state=42).sort_values("TransactionDT").reset_index(drop=True)

    print("Engineering features...")
    df = engineer_features(df)
    
    df_train, df_valid = time_based_split(df, train_frac=0.8)

    print(f"Train size: {len(df_train):,}  Valid size: {len(df_valid):,}")
    print(f"Fraud rate - train: {df_train.isFraud.mean():.3%}  valid: {df_valid.isFraud.mean():.3%}")

    model = LGBMFraudModel()
    results = model.fit(df_train, df_valid)

    print(f"\nValidation AUC : {results['val_auc']:.5f}")
    print(f"Best iteration : {results['best_iteration']}")

    model_out = root_dir / "backend" / "ml" / "artifacts" / "lgbm_fraud.pkl"
    model_out.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_out))
    print(f"Model saved -> {model_out}")

if __name__ == "__main__":
    main()
