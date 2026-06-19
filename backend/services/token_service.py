from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from backend.config import settings
from backend.models.token import TrustClaims, TrustTokenResponse


class TokenService:
    _shared_private_key: bytes | None = None
    _shared_public_key: bytes | None = None

    def __init__(self):
        if TokenService._shared_private_key is None or TokenService._shared_public_key is None:
            TokenService._shared_private_key, TokenService._shared_public_key = self._load_or_create_keys()
        self._private_key = TokenService._shared_private_key
        self._public_key = TokenService._shared_public_key

    def issue_token(self, claims: TrustClaims) -> str:
        return jwt.encode(claims.model_dump(), self._private_key, algorithm="RS256")

    def verify_token(self, token: str) -> TrustClaims:
        payload = jwt.decode(
            token,
            self._public_key,
            algorithms=["RS256"],
            options={"require": ["exp", "iat", "sub", "session_id"]},
        )
        return TrustClaims(**payload)

    def build_trust_token_response(
        self,
        claims: TrustClaims,
        step_up_required: str | None,
        explanation: list[str],
    ) -> TrustTokenResponse:
        token_str = self.issue_token(claims)
        return TrustTokenResponse(
            token=token_str,
            trust_level=claims.trust_level,
            trust_score=claims.trust_score,
            step_up_required=step_up_required,
            expires_at=datetime.fromtimestamp(claims.exp, tz=timezone.utc),
            explanation=explanation,
            session_id=claims.session_id,
        )

    @staticmethod
    def new_session_id() -> str:
        return str(uuid.uuid4())

    def _load_or_create_keys(self):
        private_path = Path(settings.TRUST_TOKEN_PRIVATE_KEY_PATH)
        public_path = Path(settings.TRUST_TOKEN_PUBLIC_KEY_PATH)

        if private_path.exists() and public_path.exists():
            return private_path.read_bytes(), public_path.read_bytes()

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        private_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return private_bytes, public_bytes
