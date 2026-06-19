from __future__ import annotations

import pickle

import numpy as np
from sklearn.ensemble import IsolationForest


class ScaledManhattanDetector:
    """
    Primary detector: Killourhy & Maxion's scaled Manhattan distance.
    For each subject, stores the mean vector and MAD (median absolute deviation)
    of their training samples. Distance to a probe sample:
        d = sum_i( |x_i - mean_i| / mad_i )
    """

    def __init__(self):
        self.subject_profiles: dict[str, dict] = {}

    def fit(self, subject_id: str, X_train: np.ndarray):
        """Build profile for one subject from their training samples."""
        mean = X_train.mean(axis=0)
        mad = np.median(np.abs(X_train - np.median(X_train, axis=0)), axis=0)
        mad = np.where(mad == 0, 1e-6, mad)  # avoid division by zero
        self.subject_profiles[subject_id] = {"mean": mean, "mad": mad}

    def score(self, subject_id: str, x_probe: np.ndarray) -> float:
        """
        Return anomaly distance similarity (higher = better match, closer to 1.0).
        Normalised to [0, 1] via sigmoid for downstream consumption.
        """
        if subject_id not in self.subject_profiles:
            return 0.5  # Neutral default for unknown/un-enrolled subject
        p = self.subject_profiles[subject_id]
        distance = np.sum(np.abs(x_probe - p["mean"]) / p["mad"])
        # normalise to 0–1 (lower distance -> higher similarity -> higher trust)
        similarity = 1.0 / (1.0 + distance / len(x_probe))
        return float(similarity)

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self.subject_profiles, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            self.subject_profiles = pickle.load(f)


class IsoForestKeystrokeDetector:
    """
    Secondary detector: Isolation Forest per-user anomaly detector.
    Used as a comparison / ensemble complement.
    """

    def __init__(self, contamination: float = 0.05):
        self.subject_models: dict[str, IsolationForest] = {}
        self.contamination = contamination

    def fit(self, subject_id: str, X_train: np.ndarray):
        iso = IsolationForest(contamination=self.contamination, random_state=42)
        iso.fit(X_train)
        self.subject_models[subject_id] = iso

    def score(self, subject_id: str, x_probe: np.ndarray) -> float:
        if subject_id not in self.subject_models:
            return 0.5
        iso = self.subject_models[subject_id]
        raw = iso.decision_function(x_probe.reshape(1, -1))[0]
        # raw is typically in [-0.5, 0.5]; normalise to [0, 1]
        return float(max(0.0, min(1.0, raw + 0.5)))


def compute_eer(genuine_scores: np.ndarray, impostor_scores: np.ndarray) -> float:
    """
    Compute Equal Error Rate.
    At EER, False Acceptance Rate (FAR) == False Rejection Rate (FRR).
    Lower EER is better.
    """
    thresholds = np.linspace(0, 1, 1000)
    for thresh in thresholds:
        far = np.mean(impostor_scores >= thresh)
        frr = np.mean(genuine_scores < thresh)
        if far <= frr:
            return float((far + frr) / 2)
    return 1.0
