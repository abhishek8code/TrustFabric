from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://trustfabric:trustfabric@db:5432/trustfabric"
    REDIS_URL: str = "redis://redis:6379/0"
    TRUST_TOKEN_PRIVATE_KEY_PATH: str = "./keys/private.pem"
    TRUST_TOKEN_PUBLIC_KEY_PATH: str = "./keys/public.pem"
    TRUST_TOKEN_TTL_SECONDS: int = 300
    TRUST_TOKEN_ISSUER: str = "trustfabric.bob.in"
    STEP_UP_THRESHOLD_OTP: int = 60
    STEP_UP_THRESHOLD_BIOMETRIC: int = 35
    STEP_UP_THRESHOLD_BLOCK: int = 15
    LGBM_MODEL_PATH: str = "./backend/ml/artifacts/lgbm_fraud.pkl"
    KEYSTROKE_SCALER_PATH: str = "./backend/ml/artifacts/keystroke_scaler.pkl"
    IDENTITY_ENCODER_PATH: str = "./backend/ml/artifacts/identity_encoder.pkl"
    SHAP_BACKGROUND_SAMPLE_SIZE: int = 100
    APP_ENV: str = "development"
    SECRET_KEY: str = "change_me_in_production"

    @property
    def private_key_path(self) -> Path:
        return Path(self.TRUST_TOKEN_PRIVATE_KEY_PATH)

    @property
    def public_key_path(self) -> Path:
        return Path(self.TRUST_TOKEN_PUBLIC_KEY_PATH)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
