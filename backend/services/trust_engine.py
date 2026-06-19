from __future__ import annotations

from dataclasses import dataclass, field

from backend.config import settings


@dataclass
class TrustSignals:
    biometric_score: float = 0.0
    is_known_device: bool = True
    is_vpn_or_tor: bool = False
    tx_fraud_probability: float = 0.0
    graph_community_risk: float = 0.0
    step_up_completions: list[str] = field(default_factory=list)
    online_adjustment: float = 0.0
    fraud_signals: list[str] = field(default_factory=list)


class TrustEngine:
    WEIGHTS = {"biometric": 20, "device": 15, "transaction": 25, "graph": 20, "step_up": 10, "online": 10}
    BASE = 50

    def compute_trust_score(self, signals: TrustSignals) -> tuple[float, str, list[str]]:
        score = self.BASE
        explanation: list[str] = []

        bio_delta = (signals.biometric_score - 0.5) * 2 * self.WEIGHTS["biometric"]
        score += bio_delta
        if signals.biometric_score < 0.4:
            explanation.append("Typing pattern does not match your usual behaviour")
        elif signals.biometric_score > 0.7:
            explanation.append("Typing pattern verified ✓")

        if not signals.is_known_device:
            score -= self.WEIGHTS["device"]
            explanation.append("Login from an unrecognised device")
        if signals.is_vpn_or_tor:
            score -= self.WEIGHTS["device"] * 0.5
            explanation.append("VPN or anonymising network detected")

        score += -(signals.tx_fraud_probability * self.WEIGHTS["transaction"])
        if signals.tx_fraud_probability > 0.5:
            explanation.append(f"Transaction anomaly score: {signals.tx_fraud_probability:.0%}")

        score += -(signals.graph_community_risk * self.WEIGHTS["graph"])
        if signals.graph_community_risk > 0.4:
            explanation.append("Account linked to a flagged network of entities")

        step_up_bonus = min(len(signals.step_up_completions), 2) * self.WEIGHTS["step_up"]
        score += step_up_bonus
        for su in signals.step_up_completions:
            explanation.append(f"{su} verification completed ✓")

        score += signals.online_adjustment
        explanation.extend(signals.fraud_signals)

        score = max(0.0, min(100.0, score))
        return round(score, 2), self._level(score), explanation

    @staticmethod
    def _level(score: float) -> str:
        if score >= settings.STEP_UP_THRESHOLD_OTP + 15:
            return "HIGH"
        if score >= settings.STEP_UP_THRESHOLD_OTP:
            return "MEDIUM"
        if score >= settings.STEP_UP_THRESHOLD_BIOMETRIC:
            return "LOW"
        return "BLOCKED"
