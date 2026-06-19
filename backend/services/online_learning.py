from __future__ import annotations

from collections import defaultdict


class OnlineLearningService:
    def __init__(self):
        self._baseline = defaultdict(lambda: {"score": 50.0, "samples": 0})

    def update_baseline(self, customer_id: str, session_result: dict) -> None:
        current = self._baseline[customer_id]
        observed = float(session_result.get("trust_score", current["score"]))
        current["score"] = 0.9 * current["score"] + 0.1 * observed
        current["samples"] += 1

    def get_adjustment(self, customer_id: str) -> float:
        current = self._baseline[customer_id]
        return max(-10.0, min(10.0, current["score"] - 50.0))
