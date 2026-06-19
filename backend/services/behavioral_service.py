from __future__ import annotations

from pathlib import Path
import numpy as np

from backend.config import settings
from backend.ml.keystroke_model import ScaledManhattanDetector


class BehavioralService:
    def __init__(self):
        self._known_devices: dict[str, set[str]] = {}
        self._model_path = Path(settings.KEYSTROKE_SCALER_PATH)
        self._detector: ScaledManhattanDetector | None = None
        self._load_detector()
        
        # Connect to Redis with safety fallback
        self.redis_client = None
        try:
            import redis
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            print("[OK] BehavioralService connected to Redis.")
        except Exception as e:
            print(f"[WARN] Redis not available for device cache: {e}. Using in-memory device registry.")

    def _load_detector(self):
        if self._model_path.exists():
            try:
                detector = ScaledManhattanDetector()
                detector.load(str(self._model_path))
                self._detector = detector
                print("[OK] Loaded ScaledManhattanDetector keystroke profile.")
            except Exception as e:
                print(f"[WARN] Failed to load ScaledManhattanDetector: {e}")
                self._detector = None

    def score_keystrokes(self, customer_id: str, timings: list[float] | None, hold_times: list[float] | None) -> float:
        if self._detector is None:
            self._load_detector()

        timings = timings or []
        hold_times = hold_times or []
        sample = np.array(timings + hold_times, dtype=float)
        
        # If we have the 31 CMU timing features, use the trained Manhattan detector
        if self._detector and len(sample) == 31:
            subject_id = customer_id
            if subject_id not in self._detector.subject_profiles:
                # Map to default subject for demo if customer is not enrolled
                subjects = list(self._detector.subject_profiles.keys())
                subject_id = subjects[0] if subjects else None
            
            if subject_id:
                try:
                    score = self._detector.score(subject_id, sample)
                    return round(max(0.0, min(1.0, score)), 4)
                except Exception as e:
                    print(f"⚠ Keystroke score evaluation failed: {e}")

        # Fallback to spread/mean calculation
        if sample.size == 0:
            return 0.5
        spread = float(np.std(sample))
        mean = float(np.mean(sample))
        score = 1.0 - min(1.0, (spread / (mean + 1.0)) * 0.75)
        return round(max(0.0, min(1.0, score)), 4)

    def is_known_device(self, customer_id: str, device_fp: str | None) -> bool:
        if not device_fp:
            return False
        if self.redis_client:
            try:
                return bool(self.redis_client.sismember(f"devices:{customer_id}", device_fp))
            except Exception:
                pass
        return device_fp in self._known_devices.get(customer_id, set())

    def register_device(self, customer_id: str, device_fp: str) -> None:
        if self.redis_client:
            try:
                self.redis_client.sadd(f"devices:{customer_id}", device_fp)
                return
            except Exception:
                pass
        self._known_devices.setdefault(customer_id, set()).add(device_fp)
