import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.ml.keystroke_model import (
    ScaledManhattanDetector, IsoForestKeystrokeDetector, compute_eer
)

def main():
    root_dir = Path(__file__).resolve().parents[1]
    data_path = root_dir / "DSL-StrongPasswordData.csv"
    if not data_path.exists():
        data_path = root_dir / "data" / "raw" / "DSL-StrongPasswordData.csv"
        
    if not data_path.exists():
        print(f"ERROR: DSL-StrongPasswordData.csv not found at {data_path}")
        sys.exit(1)

    print(f"Loading CMU Keystroke data from {data_path}...")
    df = pd.read_csv(data_path)
    feature_cols = [c for c in df.columns if c not in ["subject", "sessionIndex", "rep"]]

    subjects = df["subject"].unique()
    print(f"Training on {len(subjects)} subjects, {len(feature_cols)} timing features each")

    manhattan = ScaledManhattanDetector()
    isoforest = IsoForestKeystrokeDetector()

    eer_scores = []
    for subj in subjects:
        subj_data = df[df["subject"] == subj][feature_cols].values
        others    = df[df["subject"] != subj][feature_cols].values

        # Split 70/30
        split_idx = int(len(subj_data) * 0.7)
        X_train = subj_data[:split_idx]
        X_test = subj_data[split_idx:]
        
        # Sample 200 impostors
        np.random.seed(42)
        impostor_sample = others[np.random.choice(len(others), 200, replace=False)]

        manhattan.fit(subj, X_train)
        isoforest.fit(subj, X_train)

        genuine_scores  = [manhattan.score(subj, x) for x in X_test]
        impostor_scores = [manhattan.score(subj, x) for x in impostor_sample]
        
        # Note: EER calculation expects anomaly score (higher = anomaly) or similarity (higher = match)
        # ScaleManhattan.score returns similarity (higher = match).
        # To compute EER, let's pass 1 - similarity (higher = anomaly)
        genuine_anom = 1.0 - np.array(genuine_scores)
        impostor_anom = 1.0 - np.array(impostor_scores)
        
        eer = compute_eer(genuine_anom, impostor_anom)
        eer_scores.append(eer)

    avg_eer = np.mean(eer_scores)
    print(f"Average EER (Manhattan): {avg_eer:.4f}  ({avg_eer*100:.2f}%)")

    output_dir = root_dir / "backend" / "ml" / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save Manhattan profiles to keystroke_scaler.pkl as referenced in config settings
    manhattan_path = output_dir / "keystroke_scaler.pkl"
    manhattan.save(str(manhattan_path))
    print(f"Manhattan profiles saved -> {manhattan_path}")

    # Save IsoForest models
    isoforest_path = output_dir / "keystroke_isoforest.pkl"
    with open(isoforest_path, "wb") as f:
        pickle.dump(isoforest, f)
    print(f"IsoForest models saved -> {isoforest_path}")

if __name__ == "__main__":
    main()
