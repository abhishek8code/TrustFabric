from __future__ import annotations

import random

from backend.services.trust_engine import TrustEngine, TrustSignals


class AdversarialService:
    def __init__(self, trust_engine: TrustEngine):
        self.engine = trust_engine

    def simulate_spoofed_biometrics(self) -> dict:
        biometric_score = random.uniform(0.25, 0.45)
        score, level, explanation = self.engine.compute_trust_score(TrustSignals(biometric_score=biometric_score, is_known_device=False))
        return {"attack": "SPOOFED_BIOMETRICS", "attack_description": "Adversary submits population-average keystroke timings", "biometric_score": biometric_score, "trust_score": score, "trust_level": level, "outcome": "BLOCKED" if score < 35 else "FLAGGED", "explanation": explanation, "resilience_verdict": "✓ Detected" if score < 50 else "✗ Evaded"}

    def simulate_boiling_frog_ato(self, num_sessions: int = 15) -> list[dict]:
        results = []
        for i in range(num_sessions):
            drift = i / num_sessions
            biometric_score = max(0.1, 0.80 - drift * 0.70)
            is_known_device = i < 8
            online_adjustment = -drift * 8
            score, level, _ = self.engine.compute_trust_score(TrustSignals(biometric_score=biometric_score, is_known_device=is_known_device, online_adjustment=online_adjustment))
            results.append({"session": i + 1, "biometric_score": round(biometric_score, 3), "trust_score": round(score, 2), "trust_level": level, "step_up_triggered": score < 60})
        return results

    def simulate_graph_evasion(self) -> dict:
        community_risk = 0.67
        score, level, _ = self.engine.compute_trust_score(TrustSignals(biometric_score=0.72, is_known_device=True, graph_community_risk=community_risk))
        return {"attack": "GRAPH_EVASION", "attack_description": "Funds routed through 3 clean intermediaries before mule accounts", "community_risk_detected": community_risk, "trust_score": score, "trust_level": level, "outcome": "FLAGGED" if score < 75 else "EVADED", "resilience_verdict": "✓ Detected via graph community" if score < 75 else "✗ Evaded"}
