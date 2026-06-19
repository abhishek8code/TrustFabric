from __future__ import annotations

from typing import Any
import numpy as np

from backend.ml.identity_embedder import IdentityEmbedder

SIMILARITY_THRESHOLD_REVIEW = 0.85
SIMILARITY_THRESHOLD_BLOCK = 0.95


class IdentityService:
    def __init__(self):
        self.encoder = IdentityEmbedder()
        self._application_store: dict[str, np.ndarray] = {}
        self._load_preseeded_identities()

    def _load_preseeded_identities(self):
        preseeded = [
            {"id": "cust_001", "name": "Priya Sharma", "dob": "1994-05-12", "mobile": "9876", "pincode": "382355", "email": "gmail.com"},
            {"id": "cust_002", "name": "Arjun Patel", "dob": "1992-08-24", "mobile": "8765", "pincode": "380009", "email": "yahoo.com"},
            {"id": "cust_003", "name": "Kavita Nair", "dob": "1990-11-15", "mobile": "7654", "pincode": "682011", "email": "gmail.com"},
            {"id": "cust_004", "name": "Rohit Mehta", "dob": "1988-03-02", "mobile": "6543", "pincode": "400001", "email": "bob.co.in"},
            {"id": "cust_005", "name": "Sunita Joshi", "dob": "1995-07-30", "mobile": "5432", "pincode": "411001", "email": "gmail.com"},
            {"id": "cust_fraud_001", "name": "Rajan Kumar", "dob": "1985-01-01", "mobile": "9999", "pincode": "110001", "email": "tempmail.com"},
        ]
        for item in preseeded:
            app_dict = {
                "full_name": item["name"],
                "dob": item["dob"],
                "mobile_last4": item["mobile"],
                "pincode": item["pincode"],
                "email_domain": item["email"]
            }
            self.enroll_application(item["id"], app_dict)

    def _build_input_string(self, app: dict[str, Any]) -> str:
        name_tokens = " ".join(sorted(str(app.get("full_name", "")).lower().split()))
        return f"{name_tokens} {app.get('dob', '')} {app.get('mobile_last4', '')} {app.get('pincode', '')} {app.get('email_domain', '')}".strip()

    def enroll_application(self, application_id: str, app: dict):
        text = self._build_input_string(app)
        embedding = self.encoder.encode(text)
        self._application_store[application_id] = embedding

    def check_identity_recycling(self, app: dict) -> dict:
        if not self._application_store:
            return {
                "max_similarity": 0.0,
                "closest_match_id": None,
                "risk_level": "CLEAR",
                "explanation": "No prior applications to compare against."
            }
        
        text = self._build_input_string(app)
        probe_emb = self.encoder.encode(text)
        
        stored_ids = list(self._application_store.keys())
        stored_embs = np.stack(list(self._application_store.values()))
        
        # Batch cosine similarity (dot product of L2-normalized embeddings)
        sims = stored_embs @ probe_emb
        max_idx = int(np.argmax(sims))
        max_sim = float(sims[max_idx])
        closest_id = stored_ids[max_idx]
        
        if max_sim >= SIMILARITY_THRESHOLD_BLOCK:
            risk_level = "BLOCK"
            explanation = f"Near-identical identity fingerprint detected (similarity {max_sim:.2f}). Likely duplicate application."
        elif max_sim >= SIMILARITY_THRESHOLD_REVIEW:
            risk_level = "REVIEW"
            explanation = f"Partial identity match with existing application {closest_id} (similarity {max_sim:.2f}). Manual review required."
        else:
            risk_level = "CLEAR"
            explanation = f"No significant identity overlap detected (max similarity {max_sim:.2f})."
            
        return {
            "max_similarity": round(max_sim, 4),
            "closest_match_id": closest_id if max_sim >= SIMILARITY_THRESHOLD_REVIEW else None,
            "risk_level": risk_level,
            "explanation": explanation
        }
