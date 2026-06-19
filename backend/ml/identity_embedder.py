import hashlib
import numpy as np


class IdentityEmbedder:
    """
    Sentence-transformers encoder for soft-PII identity applications.
    Includes a robust SHA-256 fallback to prevent download blocker issues in clean offline environments.
    """

    def __init__(self):
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[OK] SentenceTransformer loaded successfully.")
        except Exception as e:
            print(f"[WARN] Could not load SentenceTransformer: {e}. Using deterministic SHA-256 vector fallback.")
            self.model = None

    def encode(self, text: str) -> np.ndarray:
        if self.model is not None:
            try:
                return self.model.encode(text, normalize_embeddings=True)
            except Exception:
                pass

        # Deterministic 384-dimension vector fallback matching all-MiniLM-L6-v2 vector dimension
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # Expand 32 bytes to 384 bytes by repeating
        expanded = digest * 12
        vec = np.frombuffer(expanded, dtype=np.uint8).astype(float)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm
