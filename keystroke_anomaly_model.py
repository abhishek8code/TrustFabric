"""
CMU Keystroke Dynamics Benchmark Dataset -> Behavioral-Biometric Detector
=============================================================================
Detector role in the Identity Trust Engine: Stage 3, "Behavioral Anomaly
Detection" sub-score (biometric channel), covering Behavioral Anomalies +
New Device Risk + Account Takeover.

Unlike IEEE-CIS, there is no "fraud" label here -- the task is per-user
anomaly detection: does this typing sample match subject X's own enrolled
baseline? This is a direct stand-in for "anomalous = relative to THIS
customer, not the population" from your Stage 2 feature-store design.

Dataset: https://www.cs.cmu.edu/~keystroke/
Direct CSV: https://www.cs.cmu.edu/~keystroke/DSL-StrongPasswordData.csv
Download it and update DATA_PATH below.

Install deps:
    pip install pandas numpy scikit-learn --break-system-packages
"""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from sklearn.ensemble import IsolationForest

DATA_PATH = "./data/DSL-StrongPasswordData.csv"

# Standard evaluation protocol from the original Killourhy & Maxion (2009)
# benchmark study: first N_TRAIN_SESSIONS (of 8 total, 50 reps each) are
# used to enroll/baseline a subject; remaining genuine sessions + a sample
# of every other subject's typing are the test set.
N_TRAIN_SESSIONS = 4
IMPOSTOR_SAMPLES_PER_SUBJECT = 5


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
def load_data(path: str = DATA_PATH):
    df = pd.read_csv(path)
    feature_cols = [c for c in df.columns if c not in ("subject", "sessionIndex", "rep")]
    return df, feature_cols


# ---------------------------------------------------------------------------
# 2. PER-SUBJECT ENROLLMENT / TEST SPLIT
# ---------------------------------------------------------------------------
def split_subject(df, subject, feature_cols, n_train_sessions=N_TRAIN_SESSIONS):
    subj_df = df[df["subject"] == subject]

    train = subj_df[subj_df["sessionIndex"] <= n_train_sessions][feature_cols].values
    genuine_test = subj_df[subj_df["sessionIndex"] > n_train_sessions][feature_cols].values

    impostor_df = df[df["subject"] != subject]
    impostor_test = (
        impostor_df.groupby("subject")
        .head(IMPOSTOR_SAMPLES_PER_SUBJECT)[feature_cols]
        .values
    )
    return train, genuine_test, impostor_test


# ---------------------------------------------------------------------------
# 3. DETECTORS
# ---------------------------------------------------------------------------
def scaled_manhattan_detector(train, genuine_test, impostor_test):
    """
    Per-feature normalized distance to the subject's own mean typing
    rhythm. Despite its simplicity this was one of the strongest
    performers in the original benchmark study -- a good first model
    to ship before reaching for anything fancier.
    """
    mean = train.mean(axis=0)
    mad = np.mean(np.abs(train - mean), axis=0) + 1e-9  # mean absolute deviation

    def score(samples):
        return np.sum(np.abs(samples - mean) / mad, axis=1)

    return score(genuine_test), score(impostor_test)


def mahalanobis_detector(train, genuine_test, impostor_test):
    """Accounts for correlations between timing features."""
    mean = train.mean(axis=0)
    cov = np.cov(train, rowvar=False) + np.eye(train.shape[1]) * 1e-6
    inv_cov = np.linalg.pinv(cov)

    def score(samples):
        diff = samples - mean
        return np.einsum("ij,jk,ik->i", diff, inv_cov, diff)

    return score(genuine_test), score(impostor_test)


def isolation_forest_detector(train, genuine_test, impostor_test):
    """The 'ML-flavored' alternative -- good to show alongside the
    classical baselines for comparison in your pitch deck."""
    clf = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
    clf.fit(train)
    genuine_scores = -clf.score_samples(genuine_test)   # higher = more anomalous
    impostor_scores = -clf.score_samples(impostor_test)
    return genuine_scores, impostor_scores


# ---------------------------------------------------------------------------
# 4. EVALUATION -- Equal Error Rate (the standard biometric metric)
# ---------------------------------------------------------------------------
def compute_eer(genuine_scores, impostor_scores):
    y_true = np.concatenate([np.zeros(len(genuine_scores)), np.ones(len(impostor_scores))])
    y_score = np.concatenate([genuine_scores, impostor_scores])
    fpr, tpr, _ = roc_curve(y_true, y_score)
    fnr = 1 - tpr
    eer_idx = np.nanargmin(np.abs(fnr - fpr))
    return (fpr[eer_idx] + fnr[eer_idx]) / 2


def evaluate_all_subjects(df, feature_cols, detector_fn, n_train_sessions=N_TRAIN_SESSIONS):
    eers = []
    for subject in df["subject"].unique():
        train, genuine_test, impostor_test = split_subject(
            df, subject, feature_cols, n_train_sessions
        )
        g_scores, i_scores = detector_fn(train, genuine_test, impostor_test)
        eers.append(compute_eer(g_scores, i_scores))
    return float(np.mean(eers)), float(np.std(eers))


# ---------------------------------------------------------------------------
# 5. LIVE-SCORE A SINGLE SESSION (useful for your demo UI)
# ---------------------------------------------------------------------------
def score_single_session(train, sample, mean=None, mad=None):
    """Returns a single behavioral-biometric anomaly score for one typing
    sample, using the scaled-Manhattan detector. Wire this into your demo's
    'live risk score' widget."""
    if mean is None:
        mean = train.mean(axis=0)
    if mad is None:
        mad = np.mean(np.abs(train - mean), axis=0) + 1e-9
    return float(np.sum(np.abs(sample - mean) / mad))


if __name__ == "__main__":
    print("Loading data...")
    df, feature_cols = load_data()

    detectors = [
        ("Scaled Manhattan", scaled_manhattan_detector),
        ("Mahalanobis", mahalanobis_detector),
        ("Isolation Forest", isolation_forest_detector),
    ]

    print(f"\nEvaluating across all {df['subject'].nunique()} subjects "
          f"(EER = lower is better):\n")
    for name, fn in detectors:
        mean_eer, std_eer = evaluate_all_subjects(df, feature_cols, fn)
        print(f"  {name:20s}: mean EER = {mean_eer*100:5.2f}%  (+/- {std_eer*100:.2f}%)")
