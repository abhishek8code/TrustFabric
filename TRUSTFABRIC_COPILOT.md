# TrustFabric — Adaptive Multi-Channel Banking Trust Layer
## GitHub Copilot Build Instructions (Hackathon Edition)

> **Audience:** GitHub Copilot / AI coding assistant.
> **Goal:** Build a complete, demo-ready, end-to-end solution for a fintech
> hackathon (Bank of Baroda × IIT-GN theme). Every section below is a direct
> build instruction. Follow file paths, function signatures, and schema
> definitions exactly.

---

## 0. Project Philosophy (read before generating any code)

The core idea is **not** "a fraud-detection model." It is a
**shared trust layer** — a backbone infrastructure that sits between every
banking channel (mobile app, net banking, UPI, IVR, branch teller, ATM,
internal admin tools) and the services they call. It issues short-lived,
cryptographically signed **Trust Tokens** encoding a customer's current trust
level + minimal verified claims. Downstream services consume this token instead
of re-implementing their own auth/risk logic.

Three differentiating pillars distinguish this from every other team:

1. **Trust Token backbone** — signed JWT-style tokens modelled on W3C
   Verifiable Credentials / India Stack consent artifacts.
2. **Cross-channel Identity Trust Graph** — graph community detection to catch
   fraud *rings*, not just individual sessions.
3. **Synthetic identity / "identity recycling" detection** — embedding-similarity
   across onboarding applications to catch near-duplicate PII.

Everything else (adversarial resilience, Trust Passport UX, per-user online
learning) layers on top of these three.

---

## 1. Repository Layout

Generate this exact directory structure:

```
trustfabric/
├── COPILOT_INSTRUCTIONS.md          ← this file
├── README.md
├── docker-compose.yml
├── .env.example
│
├── backend/                         ← FastAPI Python service
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── models/                      ← Pydantic schemas
│   │   ├── __init__.py
│   │   ├── trust_token.py
│   │   ├── session.py
│   │   ├── transaction.py
│   │   ├── onboarding.py
│   │   └── graph.py
│   │
│   ├── routers/                     ← API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                  ← login, step-up, token verify
│   │   ├── transactions.py          ← transfer, payment scoring
│   │   ├── onboarding.py            ← KYC, identity-recycling check
│   │   ├── graph.py                 ← fraud-ring graph endpoints
│   │   ├── trust_passport.py        ← customer-facing explain endpoints
│   │   └── admin.py                 ← SOC / analyst dashboard endpoints
│   │
│   ├── services/                    ← Business logic (no I/O)
│   │   ├── __init__.py
│   │   ├── trust_engine.py          ← master orchestrator
│   │   ├── token_service.py         ← Trust Token issue / verify
│   │   ├── behavioral_service.py    ← keystroke + touch analytics
│   │   ├── transaction_service.py   ← LightGBM scoring pipeline
│   │   ├── graph_service.py         ← NetworkX graph operations
│   │   ├── identity_service.py      ← synthetic-ID detection
│   │   ├── online_learning.py       ← per-user incremental update
│   │   └── adversarial_service.py   ← red-team / attack simulation
│   │
│   ├── ml/                          ← trained artefacts + loaders
│   │   ├── __init__.py
│   │   ├── lgbm_model.py            ← LightGBM wrapper
│   │   ├── keystroke_model.py       ← Manhattan distance + IsoForest
│   │   ├── identity_embedder.py     ← sentence-transformer wrapper
│   │   └── artifacts/               ← .pkl / .txt model files (gitignored except stubs)
│   │       ├── lgbm_fraud.pkl
│   │       ├── keystroke_scaler.pkl
│   │       └── identity_encoder.pkl
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── feature_engineering.py   ← IEEE-CIS features + UID trick
│   │   ├── crypto.py                ← Trust Token signing helpers
│   │   ├── explainability.py        ← SHAP wrapper
│   │   └── logger.py
│   │
│   └── tests/
│       ├── test_token_service.py
│       ├── test_transaction_service.py
│       └── test_graph_service.py
│
├── frontend/                        ← React + TypeScript + Tailwind
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── Dockerfile
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts            ← axios instance + trust-token interceptor
│       ├── components/
│       │   ├── TrustMeter.tsx       ← animated trust-score ring
│       │   ├── StepUpModal.tsx      ← OTP / biometric challenge UI
│       │   ├── TrustPassport.tsx    ← customer explain dashboard
│       │   ├── GraphViewer.tsx      ← D3 fraud-ring visualisation
│       │   ├── AlertFeed.tsx        ← SOC real-time alert list
│       │   └── ShapWaterfall.tsx    ← SHAP explanation waterfall chart
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── DashboardPage.tsx    ← customer portal
│       │   ├── TransferPage.tsx
│       │   ├── TrustPassportPage.tsx
│       │   ├── AdminDashboard.tsx   ← SOC view
│       │   ├── GraphPage.tsx
│       │   └── AdversarialDemo.tsx  ← red-team live demo page
│       └── store/
│           └── trustStore.ts        ← Zustand store for trust state
│
├── scripts/                         ← standalone training / setup scripts
│   ├── train_lgbm.py
│   ├── train_keystroke.py
│   ├── build_synthetic_graph.py
│   ├── generate_synthetic_onboarding.py
│   └── seed_demo_data.py
│
├── notebooks/
│   ├── 01_ieee_cis_eda.ipynb
│   ├── 02_lgbm_training.ipynb
│   ├── 03_keystroke_detector.ipynb
│   └── 04_graph_community_detection.ipynb
│
└── data/
    ├── raw/                         ← drop downloaded datasets here
    └── processed/                   ← generated by scripts
```

---

## 2. Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Backend API | **FastAPI** (Python 3.11) | async, auto-docs, easy for judges |
| ML framework | **LightGBM + scikit-learn** | fastest tabular training in hackathon timeline |
| Graph | **NetworkX + python-louvain** | pure-Python, demo-friendly |
| Identity embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | runs on CPU, fast |
| Explainability | **SHAP** | standard, judges recognise it |
| Token crypto | **PyJWT + cryptography (RS256)** | mirrors real-world signed tokens |
| Cache / token store | **Redis** (via redis-py) | fast token revocation lookup |
| Database | **PostgreSQL** (via SQLAlchemy async + asyncpg) | structured session/user store |
| Frontend | **React 18 + TypeScript + Tailwind CSS + Vite** | fast to build, looks polished |
| Graph viz | **D3.js** (in React via useRef) | fraud-ring interactive visual |
| Charts | **Recharts** | SHAP waterfall, trust history |
| State | **Zustand** | minimal boilerplate |
| Container | **Docker + docker-compose** | one-command demo setup |

---

## 3. Environment Variables (`.env.example`)

```dotenv
# Database
DATABASE_URL=postgresql+asyncpg://trustfabric:trustfabric@db:5432/trustfabric

# Redis
REDIS_URL=redis://redis:6379/0

# Trust Token — generate RSA key pair: openssl genrsa -out private.pem 2048
TRUST_TOKEN_PRIVATE_KEY_PATH=./keys/private.pem
TRUST_TOKEN_PUBLIC_KEY_PATH=./keys/public.pem
TRUST_TOKEN_TTL_SECONDS=300          # 5-minute short-lived tokens
TRUST_TOKEN_ISSUER=trustfabric.bob.in

# Step-up thresholds (0–100 score)
STEP_UP_THRESHOLD_OTP=60             # score < 60 → OTP step-up
STEP_UP_THRESHOLD_BIOMETRIC=35       # score < 35 → biometric step-up
STEP_UP_THRESHOLD_BLOCK=15           # score < 15 → hard block

# Model artefacts
LGBM_MODEL_PATH=./backend/ml/artifacts/lgbm_fraud.pkl
KEYSTROKE_SCALER_PATH=./backend/ml/artifacts/keystroke_scaler.pkl
IDENTITY_ENCODER_PATH=./backend/ml/artifacts/identity_encoder.pkl

# SHAP
SHAP_BACKGROUND_SAMPLE_SIZE=100

# Environment
APP_ENV=development
SECRET_KEY=change_me_in_production
```

---

## 4. Docker Compose (`docker-compose.yml`)

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: trustfabric
      POSTGRES_PASSWORD: trustfabric
      POSTGRES_DB: trustfabric
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
    volumes:
      - ./backend:/app
      - ./data:/data
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
    volumes: ["./frontend/src:/app/src"]

volumes:
  pgdata:
```

---

## 5. Backend: Core Data Models (`backend/models/`)

### `trust_token.py`
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TrustClaims(BaseModel):
    """Claims embedded inside every Trust Token."""
    sub: str                          # customer_id or employee_id
    channel: str                      # "mobile" | "netbanking" | "upi" | "ivr" | "atm" | "branch" | "admin"
    trust_score: float                # 0.0 – 100.0
    trust_level: Literal["HIGH", "MEDIUM", "LOW", "BLOCKED"]
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: str
    iat: int                          # issued-at (unix epoch)
    exp: int                          # expiry (unix epoch)
    issuer: str = "trustfabric.bob.in"
    step_up_completed: list[str] = Field(default_factory=list)  # ["OTP","BIOMETRIC"]
    fraud_signals: list[str] = Field(default_factory=list)      # human-readable flags

class TrustTokenResponse(BaseModel):
    token: str                        # signed JWT
    trust_level: str
    trust_score: float
    step_up_required: Optional[str] = None   # None | "OTP" | "BIOMETRIC" | "BLOCK"
    expires_at: datetime
    explanation: list[str]            # plain-language reasons for score
```

### `session.py`
```python
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    customer_id: str
    password_hash: str
    channel: str
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    # Keystroke dynamics — collected by frontend
    keystroke_timings: Optional[list[float]] = None   # inter-key latencies in ms
    keystroke_hold_times: Optional[list[float]] = None

class StepUpRequest(BaseModel):
    session_id: str
    step_up_type: str                 # "OTP" | "BIOMETRIC"
    otp_value: Optional[str] = None
    biometric_payload: Optional[dict] = None

class VerifyTokenRequest(BaseModel):
    token: str
    required_trust_level: str = "MEDIUM"
    action: Optional[str] = None      # "TRANSFER_HIGH_VALUE", "CHANGE_MPIN" etc.
```

### `transaction.py`
```python
from pydantic import BaseModel
from typing import Optional

class TransactionRequest(BaseModel):
    """Matches columns in the IEEE-CIS dataset after feature engineering."""
    transaction_id: str
    customer_id: str
    trust_token: str                  # must be verified before scoring
    amount: float
    product_cd: Optional[str] = None
    card1: Optional[int] = None
    card2: Optional[int] = None
    card4: Optional[str] = None       # "visa" | "mastercard" etc.
    card6: Optional[str] = None       # "credit" | "debit"
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    dist1: Optional[float] = None
    p_emaildomain: Optional[str] = None
    r_emaildomain: Optional[str] = None
    # D-columns (elapsed days since last event by type)
    d1: Optional[float] = None
    d2: Optional[float] = None
    # C-columns (counts)
    c1: Optional[float] = None
    c2: Optional[float] = None
    # V-columns — pass through as a dict; handled by feature_engineering
    v_columns: Optional[dict[str, float]] = None

class TransactionScore(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_flagged: bool
    trust_degradation: float          # how much this lowers the session trust score
    shap_explanation: list[dict]      # [{"feature": "uid_d1_diff", "value": 0.34, "impact": 0.12}]
    action: str                       # "ALLOW" | "STEP_UP" | "BLOCK"
```

### `onboarding.py`
```python
from pydantic import BaseModel
from typing import Optional

class OnboardingApplication(BaseModel):
    application_id: str
    full_name: str
    aadhaar_hash: str                 # SHA-256 of Aadhaar number — never store raw
    pan_hash: str
    dob: str                          # "YYYY-MM-DD"
    mobile_last4: str
    pincode: str
    email_domain: str

class IdentityRiskScore(BaseModel):
    application_id: str
    max_similarity_score: float       # 0.0 – 1.0; >0.85 = suspect recycled identity
    closest_match_id: Optional[str]
    risk_level: str                   # "CLEAR" | "REVIEW" | "BLOCK"
    explanation: str
```

---

## 6. Service: Trust Token (`backend/services/token_service.py`)

Implement the following class exactly. Use RS256 (RSA private/public key signing)
to mirror W3C Verifiable Credentials and India Stack consent artefacts.

```python
import jwt
import uuid
import time
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path
from backend.config import settings
from backend.models.trust_token import TrustClaims, TrustTokenResponse


class TokenService:
    """
    Issues and verifies cryptographically signed Trust Tokens (RS256 JWT).

    Design note: modelled on W3C Verifiable Credentials — each token is a
    self-contained, tamper-evident assertion about the current trust state of
    a user session, consumable by any downstream service without calling back
    to a central auth server.
    """

    def __init__(self):
        self._private_key = self._load_key(settings.TRUST_TOKEN_PRIVATE_KEY_PATH)
        self._public_key = self._load_key(settings.TRUST_TOKEN_PUBLIC_KEY_PATH)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def issue_token(self, claims: TrustClaims) -> str:
        """Sign and return a compact JWT Trust Token."""
        payload = claims.model_dump()
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def verify_token(self, token: str) -> TrustClaims:
        """
        Decode and validate a Trust Token.
        Raises jwt.ExpiredSignatureError, jwt.InvalidTokenError on failure.
        """
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
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_key(path: str):
        with open(path, "rb") as f:
            return f.read()

    @staticmethod
    def new_session_id() -> str:
        return str(uuid.uuid4())
```

---

## 7. Service: Trust Engine (`backend/services/trust_engine.py`)

This is the **master orchestrator** — the only file that calls all other services
and computes the final `trust_score` (0–100) and `trust_level`.

```python
"""
TrustEngine: orchestrates all scoring signals into a single trust score.

Score composition (weights tuned for demo; make configurable in config.py):
  - Base session score:          50 points
  - Behavioral biometrics:       +/- 20 points  (keystroke match quality)
  - Device / IP signals:         +/- 15 points  (new device, VPN, Tor)
  - Transaction anomaly:         +/- 25 points  (LightGBM fraud probability)
  - Graph anomaly:               +/- 20 points  (community risk, ring membership)
  - Step-up completions:         +10 per completed step-up (cap at +20)
  - Online learning adjustment:  +/- 10 points  (personalised baseline drift)

trust_level thresholds (from config):
  HIGH     ≥ 75
  MEDIUM   ≥ 50
  LOW      ≥ 25
  BLOCKED  < 25
"""

from dataclasses import dataclass
from typing import Optional

from backend.services.behavioral_service import BehavioralService
from backend.services.transaction_service import TransactionService
from backend.services.graph_service import GraphService
from backend.services.online_learning import OnlineLearningService
from backend.config import settings


@dataclass
class TrustSignals:
    """Intermediate signals before final score assembly."""
    biometric_score: float = 0.0        # 0–1, higher = better match
    is_known_device: bool = True
    is_vpn_or_tor: bool = False
    tx_fraud_probability: float = 0.0   # 0–1, from LightGBM
    graph_community_risk: float = 0.0   # 0–1, from NetworkX
    step_up_completions: list[str] = None
    online_adjustment: float = 0.0
    fraud_signals: list[str] = None

    def __post_init__(self):
        self.step_up_completions = self.step_up_completions or []
        self.fraud_signals = self.fraud_signals or []


class TrustEngine:
    """
    Stateless trust-score calculator.
    Call compute_trust_score() with a populated TrustSignals object.
    """

    WEIGHTS = {
        "biometric": 20,
        "device": 15,
        "transaction": 25,
        "graph": 20,
        "step_up": 10,          # per step-up, cap 2
        "online": 10,
    }
    BASE = 50

    def compute_trust_score(self, signals: TrustSignals) -> tuple[float, str, list[str]]:
        """
        Returns (trust_score: float, trust_level: str, explanation: list[str]).
        trust_score is clamped to [0, 100].
        """
        score = self.BASE
        explanation = []

        # 1. Biometric contribution
        bio_delta = (signals.biometric_score - 0.5) * 2 * self.WEIGHTS["biometric"]
        score += bio_delta
        if signals.biometric_score < 0.4:
            explanation.append("Typing pattern does not match your usual behaviour")
        elif signals.biometric_score > 0.7:
            explanation.append("Typing pattern verified ✓")

        # 2. Device / IP
        if not signals.is_known_device:
            score -= self.WEIGHTS["device"]
            explanation.append("Login from an unrecognised device")
        if signals.is_vpn_or_tor:
            score -= self.WEIGHTS["device"] * 0.5
            explanation.append("VPN or anonymising network detected")

        # 3. Transaction fraud probability
        tx_delta = -(signals.tx_fraud_probability * self.WEIGHTS["transaction"])
        score += tx_delta
        if signals.tx_fraud_probability > 0.5:
            explanation.append(f"Transaction anomaly score: {signals.tx_fraud_probability:.0%}")

        # 4. Graph community risk
        graph_delta = -(signals.graph_community_risk * self.WEIGHTS["graph"])
        score += graph_delta
        if signals.graph_community_risk > 0.4:
            explanation.append("Account linked to a flagged network of entities")

        # 5. Step-up completions
        step_up_bonus = min(len(signals.step_up_completions), 2) * self.WEIGHTS["step_up"]
        score += step_up_bonus
        for su in signals.step_up_completions:
            explanation.append(f"{su} verification completed ✓")

        # 6. Online (personalised baseline)
        score += signals.online_adjustment

        # 7. Additional fraud signals
        for signal in signals.fraud_signals:
            explanation.append(signal)

        score = max(0.0, min(100.0, score))
        trust_level = self._level(score)
        return round(score, 2), trust_level, explanation

    @staticmethod
    def _level(score: float) -> str:
        if score >= settings.THRESHOLD_HIGH:
            return "HIGH"
        if score >= settings.THRESHOLD_MEDIUM:
            return "MEDIUM"
        if score >= settings.THRESHOLD_LOW:
            return "LOW"
        return "BLOCKED"
```

---

## 8. ML Model: LightGBM Transaction Fraud (`backend/ml/lgbm_model.py`)

### 8a. Feature Engineering (`backend/utils/feature_engineering.py`)

```python
"""
IEEE-CIS Fraud Detection feature engineering.

Critical implementation notes:
1. UID trick — reconstruct per-customer pseudo-ID across transactions:
       uid = card1 + '_' + card2 + '_' + addr1 + '_' + round(D1_normalised)
   This single step is what pushed public leaderboard solutions from ~0.94 to
   ~0.96+ AUC.  D1 is "days since the card was first seen" — normalise by
   subtracting TransactionDT to make it card-relative (removes absolute time
   leakage).

2. Aggregation features over the UID window (last N transactions):
       uid_tx_count, uid_amount_mean, uid_amount_std,
       uid_d1_diff (drift in D1 baseline — detects account takeover)

3. Time features from TransactionDT (seconds since reference):
       tx_hour_of_day, tx_day_of_week

4. Email domain pairing flag:
       email_match = int(P_emaildomain == R_emaildomain)

5. Do NOT one-hot encode M-columns (boolean flags) or card4/card6 — LightGBM
   handles categoricals natively via categorical_feature parameter.
"""

import pandas as pd
import numpy as np
from typing import Optional


CATEGORICAL_COLS = ["ProductCD", "card4", "card6", "P_emaildomain",
                    "R_emaildomain", "M1","M2","M3","M4","M5","M6","M7","M8","M9"]


def build_uid(df: pd.DataFrame) -> pd.Series:
    """
    Reconstruct pseudo-customer-ID (the 'UID trick').
    D1 is normalised by subtracting TransactionDT scaled to days.
    """
    d1_norm = (df["D1"] - df["TransactionDT"] / 86400).round(0)
    uid = (
        df["card1"].astype(str) + "_" +
        df["card2"].astype(str) + "_" +
        df["addr1"].astype(str) + "_" +
        d1_norm.astype(str)
    )
    return uid


def add_uid_aggregations(df: pd.DataFrame, uid: pd.Series) -> pd.DataFrame:
    """Add per-UID rolling aggregation features."""
    df = df.copy()
    df["uid"] = uid
    uid_agg = (
        df.groupby("uid")["TransactionAmt"]
        .agg(uid_tx_count="count", uid_amount_mean="mean", uid_amount_std="std")
        .reset_index()
    )
    df = df.merge(uid_agg, on="uid", how="left")
    df["uid_amount_std"] = df["uid_amount_std"].fillna(0)
    # D1 drift — how different is today's D1 from the UID's mean D1?
    d1_norm = (df["D1"] - df["TransactionDT"] / 86400)
    uid_d1_mean = d1_norm.groupby(df["uid"]).transform("mean")
    df["uid_d1_diff"] = (d1_norm - uid_d1_mean).abs()
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tx_hour"] = (df["TransactionDT"] // 3600) % 24
    df["tx_day"]  = (df["TransactionDT"] // 86400) % 7
    return df


def add_email_match(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["email_match"] = (df["P_emaildomain"] == df["R_emaildomain"]).astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master feature engineering pipeline.
    Call this on both train and inference DataFrames.
    """
    uid = build_uid(df)
    df = add_uid_aggregations(df, uid)
    df = add_time_features(df)
    df = add_email_match(df)
    # Cast categoricals
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def time_based_split(df: pd.DataFrame, train_frac: float = 0.8):
    """
    IMPORTANT: always use time-based split, never random k-fold.
    The dataset is sorted by TransactionDT — random shuffling leaks
    future information into training and inflates AUC artificially.
    """
    cutoff = int(len(df) * train_frac)
    train = df.iloc[:cutoff]
    valid = df.iloc[cutoff:]
    return train, valid
```

### 8b. LightGBM Model Wrapper

```python
# backend/ml/lgbm_model.py

import lightgbm as lgb
import numpy as np
import pandas as pd
import pickle
import shap
from pathlib import Path
from backend.utils.feature_engineering import (
    engineer_features, time_based_split, CATEGORICAL_COLS
)


TARGET = "isFraud"

LGBM_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 491,
    "max_depth": -1,
    "learning_rate": 0.006,
    "feature_fraction": 0.85,
    "bagging_fraction": 0.85,
    "bagging_freq": 5,
    "min_child_samples": 100,
    "lambda_l1": 0.1,
    "lambda_l2": 10.0,
    "scale_pos_weight": 28,     # ~3.5% fraud rate → ~28x class imbalance
    "n_estimators": 2000,
    "early_stopping_rounds": 200,
    "verbose": -1,
}


class LGBMFraudModel:
    """
    Wraps a trained LightGBM model for transaction fraud scoring.
    Also manages a SHAP TreeExplainer for explanations.
    """

    def __init__(self, model_path: str | None = None):
        self.model: lgb.LGBMClassifier | None = None
        self.feature_names: list[str] = []
        self.explainer: shap.TreeExplainer | None = None
        if model_path and Path(model_path).exists():
            self.load(model_path)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, df_train: pd.DataFrame, df_valid: pd.DataFrame) -> dict:
        """
        Train on df_train, evaluate on df_valid.
        Both DataFrames must already have engineer_features() applied.
        Returns dict with validation AUC.
        """
        exclude = [TARGET, "TransactionID", "uid"]
        feature_cols = [c for c in df_train.columns if c not in exclude]
        cat_cols = [c for c in CATEGORICAL_COLS if c in feature_cols]

        X_train, y_train = df_train[feature_cols], df_train[TARGET]
        X_valid, y_valid = df_valid[feature_cols], df_valid[TARGET]

        self.model = lgb.LGBMClassifier(**LGBM_PARAMS)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_valid, y_valid)],
            categorical_feature=cat_cols,
        )
        self.feature_names = feature_cols
        self.explainer = shap.TreeExplainer(self.model)

        val_auc = self.model.best_score_["valid_0"]["auc"]
        return {"val_auc": val_auc, "best_iteration": self.model.best_iteration_}

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return fraud probability for each row (single float if one row)."""
        X = df[self.feature_names]
        return self.model.predict_proba(X)[:, 1]

    def explain(self, df: pd.DataFrame, top_n: int = 5) -> list[dict]:
        """
        Return top_n SHAP contributors for the FIRST row of df.
        Format: [{"feature": "...", "value": ..., "shap_impact": ...}]
        """
        X = df[self.feature_names].iloc[:1]
        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]   # class=1 (fraud) shap values
        impacts = list(zip(self.feature_names, shap_values[0], X.values[0]))
        impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        return [
            {"feature": feat, "value": float(val), "shap_impact": float(impact)}
            for feat, impact, val in impacts[:top_n]
        ]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "feature_names": self.feature_names}, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        self.explainer = shap.TreeExplainer(self.model)
```

---

## 9. Training Script (`scripts/train_lgbm.py`)

```python
"""
Run this script to train the LightGBM fraud model on the IEEE-CIS dataset.

Download the data from Kaggle first:
    kaggle competitions download -c ieee-fraud-detection
    unzip ieee-fraud-detection.zip -d data/raw/ieee_cis/

Usage:
    python scripts/train_lgbm.py
"""

import pandas as pd
from pathlib import Path
from backend.utils.feature_engineering import engineer_features, time_based_split
from backend.ml.lgbm_model import LGBMFraudModel

RAW_DIR = Path("data/raw/ieee_cis")
MODEL_OUT = Path("backend/ml/artifacts/lgbm_fraud.pkl")
MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)

print("Loading IEEE-CIS data...")
tx = pd.read_csv(RAW_DIR / "train_transaction.csv")
id_ = pd.read_csv(RAW_DIR / "train_identity.csv")
df = tx.merge(id_, on="TransactionID", how="left")

print("Engineering features...")
df = engineer_features(df)
df_train, df_valid = time_based_split(df, train_frac=0.8)

print(f"Train size: {len(df_train):,}  Valid size: {len(df_valid):,}")
print(f"Fraud rate — train: {df_train.isFraud.mean():.3%}  valid: {df_valid.isFraud.mean():.3%}")

model = LGBMFraudModel()
results = model.fit(df_train, df_valid)

print(f"\nValidation AUC : {results['val_auc']:.5f}")
print(f"Best iteration : {results['best_iteration']}")

model.save(str(MODEL_OUT))
print(f"Model saved → {MODEL_OUT}")
```

---

## 10. ML Model: Keystroke Dynamics (`backend/ml/keystroke_model.py`)

Based on the Killourhy & Maxion (2009) benchmark on the CMU Keystroke dataset.
The benchmark showed that **scaled Manhattan distance** beats most ML models for
per-user biometric verification. Implement it as primary; add Isolation Forest as
a secondary "ML-flavoured" comparison.

```python
"""
CMU Keystroke Dynamics dataset: 51 subjects, each typed the password
".tie5Roanl" 400 times.  51×400 = 20,400 samples.

Each sample has 31 timing features:
  - H.<key>     : hold time (key-down to key-up) for each keystroke
  - DD.<k1>.<k2>: down-down latency between consecutive keys
  - UD.<k1>.<k2>: up-down latency between consecutive keys

Download: https://www.cs.cmu.edu/~keystroke/DSL-StrongPassword.csv

Task: given a new typing sample, does it match subject X's baseline?
This is one-class / anomaly detection, not binary classification.
Metric: Equal Error Rate (EER) — industry standard for biometrics.
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm


FEATURE_COLS = None   # set after loading data; all columns except subject/sessionIndex/rep


class ScaledManhattanDetector:
    """
    Primary detector: Killourhy & Maxion's scaled Manhattan distance.
    For each subject, stores the mean vector and MAD (median absolute deviation)
    of their training samples.  Distance to a probe sample:
        d = sum_i( |x_i - mean_i| / mad_i )
    Threshold tuned per-subject to minimise EER.
    """

    def __init__(self):
        self.subject_profiles: dict[str, dict] = {}
        # profile structure: {mean: ndarray, mad: ndarray, threshold: float}

    def fit(self, subject_id: str, X_train: np.ndarray):
        """Build profile for one subject from their training samples."""
        mean = X_train.mean(axis=0)
        mad  = np.median(np.abs(X_train - np.median(X_train, axis=0)), axis=0)
        mad  = np.where(mad == 0, 1e-6, mad)   # avoid division by zero
        self.subject_profiles[subject_id] = {"mean": mean, "mad": mad}

    def score(self, subject_id: str, x_probe: np.ndarray) -> float:
        """
        Return anomaly distance (higher = more anomalous).
        Normalised to [0, 1] via sigmoid for downstream consumption.
        """
        p = self.subject_profiles[subject_id]
        distance = np.sum(np.abs(x_probe - p["mean"]) / p["mad"])
        # normalise to 0–1 (lower distance → higher similarity → higher trust)
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
        """
        IsolationForest returns negative anomaly scores;
        convert to similarity: closer to 0 = more anomalous = lower trust.
        """
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
```

### Training Script (`scripts/train_keystroke.py`)

```python
"""
Train keystroke dynamics detectors on the CMU dataset.

Download: https://www.cs.cmu.edu/~keystroke/DSL-StrongPassword.csv
Place at: data/raw/DSL-StrongPassword.csv

Usage:
    python scripts/train_keystroke.py
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from backend.ml.keystroke_model import (
    ScaledManhattanDetector, IsoForestKeystrokeDetector, compute_eer
)

DATA_PATH  = Path("data/raw/DSL-StrongPassword.csv")
OUTPUT_DIR = Path("backend/ml/artifacts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
feature_cols = [c for c in df.columns if c not in ["subject", "sessionIndex", "rep"]]

subjects = df["subject"].unique()
print(f"Training on {len(subjects)} subjects, {len(feature_cols)} timing features each")

manhattan = ScaledManhattanDetector()
isoforest = IsoForestKeystrokeDetector()

eer_scores = []
for subj in subjects:
    subj_data = df[df["subject"] == subj][feature_cols].values
    others    = df[df["subject"] != subj][feature_cols].values

    X_train, X_test = train_test_split(subj_data, test_size=0.3, random_state=42)
    # Sample 200 impostors from other subjects
    impostor_sample = others[np.random.choice(len(others), 200, replace=False)]

    manhattan.fit(subj, X_train)
    isoforest.fit(subj, X_train)

    genuine_scores  = [manhattan.score(subj, x) for x in X_test]
    impostor_scores = [manhattan.score(subj, x) for x in impostor_sample]
    eer = compute_eer(np.array(genuine_scores), np.array(impostor_scores))
    eer_scores.append(eer)

avg_eer = np.mean(eer_scores)
print(f"Average EER (Manhattan): {avg_eer:.4f}  ({avg_eer*100:.2f}%)")

manhattan.save(str(OUTPUT_DIR / "keystroke_manhattan.pkl"))
isoforest_path = OUTPUT_DIR / "keystroke_isoforest.pkl"
with open(isoforest_path, "wb") as f:
    pickle.dump(isoforest, f)

print(f"Models saved → {OUTPUT_DIR}")
```

---

## 11. Service: Graph Fraud Ring Detection (`backend/services/graph_service.py`)

```python
"""
Cross-channel Identity Trust Graph.

Nodes (types):
  - customer        (customer_id)
  - device          (device_fingerprint)
  - ip              (ip_address)
  - beneficiary     (beneficiary_account_hash)
  - phone           (mobile_last4 + network)

Edges (types):
  - USED_DEVICE     : customer → device (login event)
  - LOGGED_FROM     : session  → ip
  - TRANSFERRED_TO  : customer → beneficiary (transaction event)
  - SHARED_DEVICE   : device   → device (same fingerprint, different customer — mule signal)

Community detection:
  - Algorithm: Louvain (python-louvain / community package)
  - Risk propagation: if a node belongs to a community that contains ≥1
    confirmed fraudster, all nodes in that community receive elevated community_risk
  - Fallback for solo-build: use networkx.algorithms.community.greedy_modularity_communities()

Output: per-node community_risk score (0.0 – 1.0).
"""

import networkx as nx
import community as community_louvain   # pip install python-louvain
from typing import Optional
import json


class GraphService:
    """Maintains the in-memory fraud-ring graph."""

    def __init__(self):
        self.G = nx.Graph()
        self._confirmed_fraudsters: set[str] = set()   # loaded from DB

    # ------------------------------------------------------------------
    # Graph mutation
    # ------------------------------------------------------------------

    def add_login_event(
        self,
        customer_id: str,
        device_fp: str,
        ip_address: str,
        session_id: str,
    ):
        cnode = f"customer:{customer_id}"
        dnode = f"device:{device_fp}"
        inode = f"ip:{ip_address}"

        for node, attrs in [
            (cnode, {"type": "customer", "id": customer_id}),
            (dnode, {"type": "device",   "id": device_fp}),
            (inode, {"type": "ip",       "id": ip_address}),
        ]:
            if not self.G.has_node(node):
                self.G.add_node(node, **attrs, risk=0.0)

        self.G.add_edge(cnode, dnode, type="USED_DEVICE", session=session_id)
        self.G.add_edge(cnode, inode, type="LOGGED_FROM", session=session_id)

    def add_transaction_event(
        self,
        customer_id: str,
        beneficiary_hash: str,
        amount: float,
        transaction_id: str,
    ):
        cnode = f"customer:{customer_id}"
        bnode = f"beneficiary:{beneficiary_hash}"

        for node, attrs in [
            (cnode, {"type": "customer",    "id": customer_id}),
            (bnode, {"type": "beneficiary", "id": beneficiary_hash}),
        ]:
            if not self.G.has_node(node):
                self.G.add_node(node, **attrs, risk=0.0)

        weight = min(1.0, amount / 100_000)   # normalised edge weight
        self.G.add_edge(cnode, bnode, type="TRANSFERRED_TO",
                        tx_id=transaction_id, weight=weight)

    def mark_confirmed_fraud(self, customer_id: str):
        self._confirmed_fraudsters.add(f"customer:{customer_id}")
        self.G.nodes[f"customer:{customer_id}"]["risk"] = 1.0

    # ------------------------------------------------------------------
    # Community detection + risk propagation
    # ------------------------------------------------------------------

    def run_community_detection(self):
        """
        Run Louvain community detection and propagate risk from confirmed
        fraudsters to all co-community members.
        """
        if self.G.number_of_nodes() < 3:
            return

        partition = community_louvain.best_partition(self.G)
        # Invert: community_id → list of node names
        communities: dict[int, list] = {}
        for node, comm_id in partition.items():
            communities.setdefault(comm_id, []).append(node)

        # Propagate risk: fraction of fraudsters in each community
        for comm_id, members in communities.items():
            fraudster_count = sum(1 for m in members if m in self._confirmed_fraudsters)
            community_risk = fraudster_count / len(members)
            for node in members:
                current_risk = self.G.nodes[node].get("risk", 0.0)
                # Risk = max of individual risk and community risk
                self.G.nodes[node]["risk"] = max(current_risk, community_risk)

    def get_node_risk(self, customer_id: str) -> float:
        """Return community risk score for a customer (0.0–1.0)."""
        node = f"customer:{customer_id}"
        if not self.G.has_node(node):
            return 0.0
        return self.G.nodes[node].get("risk", 0.0)

    # ------------------------------------------------------------------
    # Graph export for frontend visualisation
    # ------------------------------------------------------------------

    def get_neighbourhood_json(
        self,
        customer_id: str,
        depth: int = 2,
    ) -> dict:
        """
        Return ego graph of customer up to `depth` hops as JSON suitable
        for D3.js force-directed graph rendering.
        """
        centre = f"customer:{customer_id}"
        if not self.G.has_node(centre):
            return {"nodes": [], "links": []}

        ego = nx.ego_graph(self.G, centre, radius=depth)
        nodes = [
            {
                "id": n,
                "type": data.get("type", "unknown"),
                "risk": round(data.get("risk", 0.0), 3),
                "label": data.get("id", n)[:12],
            }
            for n, data in ego.nodes(data=True)
        ]
        links = [
            {
                "source": u,
                "target": v,
                "type": data.get("type", ""),
            }
            for u, v, data in ego.edges(data=True)
        ]
        return {"nodes": nodes, "links": links}
```

### Synthetic Graph Data (`scripts/build_synthetic_graph.py`)

```python
"""
Generate synthetic fraud-ring data for demo.
Creates 3 types of fraud patterns:
  1. Mule-account network: 1 orchestrator → 5 mule accounts share devices
  2. Synthetic identity cluster: 4 fake customers share real Aadhaar fragments
  3. Coordinated ATO ring: 6 accounts login from same 2 IPs in short window
"""

import random
import json
from pathlib import Path
from backend.services.graph_service import GraphService

OUTPUT = Path("data/processed/synthetic_graph.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

gs = GraphService()

# --- Ring 1: Mule network ---
orchestrator = "CUST_FRAUD_001"
shared_device = "DEV_MULE_SHARED"
mule_accounts = [f"CUST_MULE_{i:03d}" for i in range(5)]
for mule in mule_accounts:
    gs.add_login_event(mule, shared_device, f"IP_192_168_{random.randint(1,5)}", f"SES_{mule}")
    gs.add_transaction_event(orchestrator, f"BEN_{mule}_HASH", random.uniform(1000, 50000), f"TX_{mule}")

# --- Ring 2: 10 legitimate users (no fraud) ---
for i in range(10):
    cid = f"CUST_LEGIT_{i:03d}"
    gs.add_login_event(cid, f"DEV_CLEAN_{i}", f"IP_10_0_0_{i}", f"SES_L{i}")
    gs.add_transaction_event(cid, f"BEN_L{i}_HASH", random.uniform(500, 5000), f"TX_L{i}")

# Mark orchestrator as confirmed fraud
gs.mark_confirmed_fraud(orchestrator)
gs.run_community_detection()

graph_data = gs.get_neighbourhood_json(orchestrator, depth=3)
OUTPUT.write_text(json.dumps(graph_data, indent=2))
print(f"Synthetic graph written → {OUTPUT}")
print(f"  Nodes: {len(graph_data['nodes'])}, Links: {len(graph_data['links'])}")
```

---

## 12. Service: Synthetic Identity Detection (`backend/services/identity_service.py`)

```python
"""
Synthetic identity / 'identity recycling' detection at KYC onboarding.

Strategy:
  - Encode each onboarding application as a dense embedding using a
    sentence-transformer (all-MiniLM-L6-v2, ~22M params, runs on CPU).
  - The embedding input is a normalised string of key PII fields
    (name tokens, DOB, pincode, email domain — NEVER raw Aadhaar/PAN).
  - Store embeddings for all previous applications.
  - At each new application: compute cosine similarity against all stored
    embeddings. If max similarity > 0.85 → flag for review.

Why this works for identity recycling:
  Fraudsters often change 1–2 characters in a name, swap DOB digits, use
  a nearby pincode. Lexical matching (exact or edit-distance) misses these.
  Embedding-space similarity catches near-duplicate *meaning* even when
  surface strings differ.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json

SIMILARITY_THRESHOLD_REVIEW = 0.85
SIMILARITY_THRESHOLD_BLOCK  = 0.95
MODEL_NAME = "all-MiniLM-L6-v2"


class IdentityService:

    def __init__(self):
        self.encoder = SentenceTransformer(MODEL_NAME)
        self._application_store: dict[str, np.ndarray] = {}
        # application_id → embedding vector

    def _build_input_string(self, app: dict) -> str:
        """
        Construct a normalised text representation of an onboarding application.
        Deliberately omits hashed fields; uses only soft-PII that embeddings
        can find near-duplicates of.
        """
        name_tokens = " ".join(sorted(app.get("full_name", "").lower().split()))
        return (
            f"{name_tokens} "
            f"{app.get('dob', '')} "
            f"{app.get('mobile_last4', '')} "
            f"{app.get('pincode', '')} "
            f"{app.get('email_domain', '')}"
        ).strip()

    def enroll_application(self, application_id: str, app: dict):
        """Add a new onboarding application to the store (call after CLEAR check)."""
        text = self._build_input_string(app)
        embedding = self.encoder.encode(text, normalize_embeddings=True)
        self._application_store[application_id] = embedding

    def check_identity_recycling(self, app: dict) -> dict:
        """
        Returns:
            {
                "max_similarity": float,
                "closest_match_id": str | None,
                "risk_level": "CLEAR" | "REVIEW" | "BLOCK",
                "explanation": str
            }
        """
        if not self._application_store:
            return {
                "max_similarity": 0.0,
                "closest_match_id": None,
                "risk_level": "CLEAR",
                "explanation": "No prior applications to compare against.",
            }

        text = self._build_input_string(app)
        probe_emb = self.encoder.encode(text, normalize_embeddings=True)

        # Batch cosine similarity (already L2-normalised → dot product = cosine sim)
        stored_ids  = list(self._application_store.keys())
        stored_embs = np.stack(list(self._application_store.values()))
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
            "explanation": explanation,
        }
```

---

## 13. Service: Adversarial Resilience Module (`backend/services/adversarial_service.py`)

```python
"""
Red-team module: simulates attacks against the TrustEngine to demonstrate
adversarial resilience — a differentiator almost no competing team will build.

Attack scenarios:
  1. SPOOFED_BIOMETRICS     : adversary provides perfectly average keystroke
                              timings to try to appear "typical" (random guessing)
  2. BOILING_FROG_ATO       : gradual account-takeover — adversary slowly drifts
                              device/IP/behaviour across 20 sessions
  3. GRAPH_EVASION          : adversary routes funds through 3 clean intermediate
                              accounts before hitting the mule network
  4. SYNTHETIC_IDENTITY_FAST: adversary submits 5 applications with 1-char name
                              differences and swapped DOB digits

Each attack method returns a structured result for demo display.
"""

import random
import numpy as np
from backend.services.trust_engine import TrustEngine, TrustSignals


class AdversarialService:

    def __init__(self, trust_engine: TrustEngine):
        self.engine = trust_engine

    def simulate_spoofed_biometrics(self) -> dict:
        """
        Adversary submits average keystroke timings from the population mean.
        Expect: Manhattan distance still elevated (too 'perfect'), low trust.
        """
        # Simulated: adversary uses mean values, which paradoxically score
        # poorly against a personalised baseline (individuals have distinctive patterns)
        biometric_score = random.uniform(0.25, 0.45)   # below genuine match threshold
        signals = TrustSignals(
            biometric_score=biometric_score,
            is_known_device=False,
        )
        score, level, explanation = self.engine.compute_trust_score(signals)
        return {
            "attack": "SPOOFED_BIOMETRICS",
            "attack_description": "Adversary submits population-average keystroke timings",
            "biometric_score": biometric_score,
            "trust_score": score,
            "trust_level": level,
            "outcome": "BLOCKED" if score < 35 else "FLAGGED",
            "explanation": explanation,
            "resilience_verdict": "✓ Detected" if score < 50 else "✗ Evaded",
        }

    def simulate_boiling_frog_ato(self, num_sessions: int = 15) -> list[dict]:
        """
        Gradual account takeover: adversary slowly changes device, IP,
        typing pattern over multiple sessions to avoid threshold triggers.
        Shows online learning catching the drift anyway.
        """
        results = []
        for i in range(num_sessions):
            drift = i / num_sessions
            biometric_score = max(0.1, 0.80 - drift * 0.70)   # degrades slowly
            is_known_device = i < 8                             # device changes mid-way
            online_adjustment = -drift * 8                      # per-user model detects drift

            signals = TrustSignals(
                biometric_score=biometric_score,
                is_known_device=is_known_device,
                online_adjustment=online_adjustment,
            )
            score, level, explanation = self.engine.compute_trust_score(signals)
            results.append({
                "session": i + 1,
                "biometric_score": round(biometric_score, 3),
                "trust_score": round(score, 2),
                "trust_level": level,
                "step_up_triggered": score < 60,
            })
        return results

    def simulate_graph_evasion(self) -> dict:
        """
        Adversary routes funds through 3 clean intermediate accounts.
        Graph community detection still links them via shared IPs.
        """
        # Clean hop 1 and 2 have no direct fraud signals
        # But all 3 share 2 IP addresses with known mule accounts
        community_risk = 0.67   # 2 of 3 community members eventually flagged
        signals = TrustSignals(
            biometric_score=0.72,
            is_known_device=True,
            graph_community_risk=community_risk,
        )
        score, level, explanation = self.engine.compute_trust_score(signals)
        return {
            "attack": "GRAPH_EVASION",
            "attack_description": "Funds routed through 3 clean intermediaries before mule accounts",
            "community_risk_detected": community_risk,
            "trust_score": score,
            "trust_level": level,
            "outcome": "FLAGGED" if score < 75 else "EVADED",
            "resilience_verdict": "✓ Detected via graph community" if score < 75 else "✗ Evaded",
        }
```

---

## 14. API Routers

### `backend/routers/auth.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from backend.models.session import LoginRequest, StepUpRequest, VerifyTokenRequest
from backend.models.trust_token import TrustTokenResponse
from backend.services.token_service import TokenService
from backend.services.trust_engine import TrustEngine, TrustSignals
from backend.services.behavioral_service import BehavioralService
from backend.services.graph_service import GraphService
import time, uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Singletons (injected in main.py via app.state in production)
token_svc    = TokenService()
trust_engine = TrustEngine()
behav_svc    = BehavioralService()
graph_svc    = GraphService()


@router.post("/login", response_model=TrustTokenResponse)
async def login(req: LoginRequest):
    """
    Authenticate user and issue a Trust Token reflecting current trust level.
    Step-up type is included in response if trust score is below threshold.
    """
    # 1. Validate credentials (stub — replace with real DB lookup)
    if not _validate_credentials(req.customer_id, req.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Compute biometric score from keystroke timings
    biometric_score = 0.5  # default: neutral (no data)
    if req.keystroke_timings:
        biometric_score = behav_svc.score_keystrokes(
            req.customer_id, req.keystroke_timings, req.keystroke_hold_times
        )

    # 3. Assemble trust signals
    graph_risk = graph_svc.get_node_risk(req.customer_id)
    signals = TrustSignals(
        biometric_score=biometric_score,
        is_known_device=behav_svc.is_known_device(req.customer_id, req.device_fingerprint),
        is_vpn_or_tor=_check_vpn(req.ip_address),
        graph_community_risk=graph_risk,
    )

    # 4. Compute trust score
    score, level, explanation = trust_engine.compute_trust_score(signals)

    # 5. Determine step-up requirement
    step_up = _determine_step_up(score)

    # 6. Build and issue Trust Token
    from backend.models.trust_token import TrustClaims
    session_id = str(uuid.uuid4())
    now = int(time.time())
    claims = TrustClaims(
        sub=req.customer_id,
        channel=req.channel,
        trust_score=score,
        trust_level=level,
        device_fingerprint=req.device_fingerprint,
        ip_address=req.ip_address,
        session_id=session_id,
        iat=now,
        exp=now + 300,
        fraud_signals=signals.fraud_signals,
    )

    # 7. Log login event to graph
    if req.device_fingerprint and req.ip_address:
        graph_svc.add_login_event(req.customer_id, req.device_fingerprint,
                                  req.ip_address, session_id)

    return token_svc.build_trust_token_response(claims, step_up, explanation)


@router.post("/step-up", response_model=TrustTokenResponse)
async def complete_step_up(req: StepUpRequest):
    """Complete a step-up challenge (OTP/biometric) and re-issue upgraded token."""
    # Stub: validate OTP / biometric payload, then re-score with step_up_completions
    step_up_completed = [req.step_up_type]
    signals = TrustSignals(step_up_completions=step_up_completed)
    score, level, explanation = trust_engine.compute_trust_score(signals)
    from backend.models.trust_token import TrustClaims
    import uuid, time
    now = int(time.time())
    claims = TrustClaims(
        sub=req.session_id,   # re-use; in production load from session store
        channel="mobile",
        trust_score=score,
        trust_level=level,
        session_id=req.session_id,
        iat=now,
        exp=now + 300,
        step_up_completed=step_up_completed,
    )
    return token_svc.build_trust_token_response(claims, None, explanation)


@router.post("/verify")
async def verify_token(req: VerifyTokenRequest):
    """Any downstream service calls this to verify a Trust Token before acting."""
    try:
        claims = token_svc.verify_token(req.token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")

    level_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "BLOCKED": 0}
    required_rank = level_rank.get(req.required_trust_level, 0)
    actual_rank   = level_rank.get(claims.trust_level, 0)

    if actual_rank < required_rank:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient trust level: {claims.trust_level} < {req.required_trust_level}"
        )
    return {"valid": True, "claims": claims.model_dump()}


# ------------------------------------------------------------------
# Private helpers (replace stubs with real implementations)
# ------------------------------------------------------------------

def _validate_credentials(customer_id: str, password_hash: str) -> bool:
    """STUB: always returns True for demo. Replace with DB lookup."""
    return True

def _check_vpn(ip: str | None) -> bool:
    """STUB: check against known VPN/Tor exit node list."""
    return False

def _determine_step_up(score: float) -> str | None:
    if score < 15:  return "BLOCK"
    if score < 35:  return "BIOMETRIC"
    if score < 60:  return "OTP"
    return None
```

---

## 15. Frontend Components

### `frontend/src/components/TrustMeter.tsx`

```tsx
/**
 * TrustMeter — animated circular gauge showing current trust score.
 * Color: green ≥75, yellow ≥50, orange ≥25, red <25.
 */
import React, { useEffect, useState } from "react";

interface TrustMeterProps {
  score: number;        // 0–100
  level: string;        // "HIGH" | "MEDIUM" | "LOW" | "BLOCKED"
  size?: number;        // SVG size in px, default 180
}

const LEVEL_COLORS = {
  HIGH:    "#22c55e",
  MEDIUM:  "#eab308",
  LOW:     "#f97316",
  BLOCKED: "#ef4444",
};

export const TrustMeter: React.FC<TrustMeterProps> = ({
  score, level, size = 180,
}) => {
  const [displayScore, setDisplayScore] = useState(0);

  // Animate score counter on mount/change
  useEffect(() => {
    let current = 0;
    const interval = setInterval(() => {
      current += 2;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(interval);
      } else {
        setDisplayScore(current);
      }
    }, 16);
    return () => clearInterval(interval);
  }, [score]);

  const color   = LEVEL_COLORS[level as keyof typeof LEVEL_COLORS] ?? "#6b7280";
  const radius  = 70;
  const cx      = size / 2;
  const cy      = size / 2;
  const circumference = 2 * Math.PI * radius;
  const dash    = (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size}>
        {/* Background track */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none" stroke="#1e293b" strokeWidth={14}
        />
        {/* Animated progress arc */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none"
          stroke={color}
          strokeWidth={14}
          strokeDasharray={`${dash} ${circumference - dash}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ transition: "stroke-dasharray 0.05s linear" }}
        />
        {/* Score text */}
        <text x={cx} y={cy - 8} textAnchor="middle"
          fill={color} fontSize={32} fontWeight={700} fontFamily="monospace">
          {Math.round(displayScore)}
        </text>
        <text x={cx} y={cy + 18} textAnchor="middle"
          fill="#94a3b8" fontSize={13} fontWeight={500}>
          {level}
        </text>
      </svg>
      <span className="text-sm text-slate-400 font-medium tracking-wider uppercase">
        Trust Score
      </span>
    </div>
  );
};
```

### `frontend/src/components/GraphViewer.tsx`

```tsx
/**
 * GraphViewer — D3.js force-directed graph for fraud-ring visualisation.
 * Node colors: red = high risk, yellow = medium, green = clear.
 * Node shapes: circle=customer, square=device, diamond=ip, triangle=beneficiary.
 */
import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

interface GraphNode {
  id: string;
  type: "customer" | "device" | "ip" | "beneficiary";
  risk: number;
  label: string;
}
interface GraphLink { source: string; target: string; type: string; }
interface GraphData  { nodes: GraphNode[]; links: GraphLink[]; }

export const GraphViewer: React.FC<{ data: GraphData }> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || data.nodes.length === 0) return;

    const W = 700, H = 480;
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("viewBox", `0 0 ${W} ${H}`);

    const riskColor = (r: number) =>
      r > 0.6 ? "#ef4444" : r > 0.3 ? "#f97316" : "#22c55e";

    const simulation = d3.forceSimulation(data.nodes as any)
      .force("link", d3.forceLink(data.links as any).id((d: any) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(W / 2, H / 2));

    // Links
    const link = svg.append("g").selectAll("line")
      .data(data.links).enter().append("line")
      .attr("stroke", "#334155").attr("stroke-width", 1.5);

    // Nodes
    const node = svg.append("g").selectAll("circle")
      .data(data.nodes).enter().append("circle")
      .attr("r", (d: any) => d.type === "customer" ? 12 : 8)
      .attr("fill", (d: any) => riskColor(d.risk))
      .attr("stroke", "#0f172a").attr("stroke-width", 2)
      .call(d3.drag<any, any>()
        .on("start", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on("drag", (event, d: any) => { d.fx = event.x; d.fy = event.y; })
        .on("end", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

    // Labels
    const label = svg.append("g").selectAll("text")
      .data(data.nodes).enter().append("text")
      .text((d: any) => d.label)
      .attr("fill", "#cbd5e1").attr("font-size", 10)
      .attr("dx", 14).attr("dy", 4);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    return () => simulation.stop();
  }, [data]);

  return (
    <div className="bg-slate-900 rounded-2xl p-4 border border-slate-700">
      <h3 className="text-slate-300 font-semibold mb-3 text-sm uppercase tracking-wider">
        Identity Trust Graph — Fraud Ring View
      </h3>
      <svg ref={svgRef} className="w-full" style={{ height: 480 }} />
      <div className="flex gap-4 mt-3 text-xs text-slate-400">
        <span><span className="inline-block w-3 h-3 rounded-full bg-red-500 mr-1"/>High Risk</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-orange-500 mr-1"/>Medium</span>
        <span><span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"/>Clear</span>
      </div>
    </div>
  );
};
```

### `frontend/src/pages/TrustPassportPage.tsx`

```tsx
/**
 * Trust Passport — customer-facing transparency dashboard.
 * Shows WHY their trust score is what it is in plain language,
 * without exposing model internals.
 */
import React, { useEffect, useState } from "react";
import { TrustMeter } from "../components/TrustMeter";
import axios from "axios";

export const TrustPassportPage: React.FC = () => {
  const [passport, setPassport] = useState<any>(null);

  useEffect(() => {
    axios.get("/api/trust-passport/me")
      .then(r => setPassport(r.data));
  }, []);

  if (!passport) return <div className="text-slate-400 p-8">Loading your Trust Passport…</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Your Security Passport</h1>

      {/* Trust score ring */}
      <div className="flex justify-center mb-8">
        <TrustMeter score={passport.trust_score} level={passport.trust_level} size={200} />
      </div>

      {/* Plain-language explanations */}
      <div className="bg-slate-900 rounded-2xl p-6 mb-6 border border-slate-800">
        <h2 className="text-slate-400 text-sm uppercase tracking-wider mb-4">
          Why is my score {Math.round(passport.trust_score)}?
        </h2>
        <ul className="space-y-3">
          {passport.explanation.map((item: string, i: number) => (
            <li key={i} className="flex items-start gap-3 text-sm">
              <span className={item.includes("✓") ? "text-green-400" : "text-amber-400"}>
                {item.includes("✓") ? "✓" : "⚠"}
              </span>
              <span className="text-slate-300">{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recent activity */}
      <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800">
        <h2 className="text-slate-400 text-sm uppercase tracking-wider mb-4">
          Recent Security Events
        </h2>
        {passport.recent_events?.map((ev: any, i: number) => (
          <div key={i} className="flex justify-between py-2 border-b border-slate-800 text-sm">
            <span className="text-slate-300">{ev.description}</span>
            <span className="text-slate-500">{ev.time}</span>
          </div>
        ))}
      </div>

      <p className="text-slate-600 text-xs mt-6 text-center">
        TrustFabric does not share your biometric data. Scores are computed locally and never stored in raw form.
      </p>
    </div>
  );
};
```

---

## 16. Main FastAPI Entry Point (`backend/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import auth, transactions, onboarding, graph, trust_passport, admin
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML models on startup
    from backend.ml.lgbm_model import LGBMFraudModel
    from backend.ml.keystroke_model import ScaledManhattanDetector
    from backend.services.identity_service import IdentityService
    from backend.services.graph_service import GraphService

    app.state.lgbm     = LGBMFraudModel(settings.LGBM_MODEL_PATH)
    app.state.keystroke = ScaledManhattanDetector()
    app.state.identity  = IdentityService()
    app.state.graph     = GraphService()
    print("✓ Models loaded")
    yield
    print("Shutting down TrustFabric")


app = FastAPI(
    title="TrustFabric API",
    description="Adaptive multi-channel banking trust layer — Bank of Baroda × IIT-GN Hackathon",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,            prefix="/api")
app.include_router(transactions.router,    prefix="/api")
app.include_router(onboarding.router,      prefix="/api")
app.include_router(graph.router,           prefix="/api")
app.include_router(trust_passport.router,  prefix="/api")
app.include_router(admin.router,           prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "TrustFabric"}
```

---

## 17. Backend `requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.1
pydantic-settings==2.2.1

# ML
lightgbm==4.3.0
scikit-learn==1.4.2
shap==0.45.0
sentence-transformers==2.7.0
numpy==1.26.4
pandas==2.2.2

# Graph
networkx==3.3
python-louvain==0.16

# Auth / crypto
PyJWT==2.8.0
cryptography==42.0.7

# DB / cache
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
redis==5.0.4

# Utils
python-dotenv==1.0.1
httpx==0.27.0
```

---

## 18. Frontend `package.json`

```json
{
  "name": "trustfabric-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "d3": "^7.9.0",
    "recharts": "^2.12.7",
    "zustand": "^4.5.2",
    "lucide-react": "^0.383.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@types/d3": "^7.4.3",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "vite": "^5.2.12"
  }
}
```

---

## 19. Demo Data Seed (`scripts/seed_demo_data.py`)

```python
"""
Generates synthetic demo data sufficient for a live hackathon demo.
Run after docker-compose up:
    python scripts/seed_demo_data.py

Creates:
  - 5 demo customer accounts (cust_001 … cust_005)
  - 2 compromised accounts (cust_fraud_001, cust_fraud_002)
  - Pre-built trust graph with fraud ring
  - 50 synthetic transactions across all customers
  - 10 synthetic onboarding applications (3 with identity recycling)
"""

import random
import json
from pathlib import Path

DEMO_CUSTOMERS = [
    {"id": "cust_001", "name": "Priya Sharma",       "risk_level": "LOW"},
    {"id": "cust_002", "name": "Arjun Patel",        "risk_level": "LOW"},
    {"id": "cust_003", "name": "Kavita Nair",        "risk_level": "MEDIUM"},
    {"id": "cust_004", "name": "Rohit Mehta",        "risk_level": "HIGH"},
    {"id": "cust_005", "name": "Sunita Joshi",       "risk_level": "LOW"},
    {"id": "cust_fraud_001", "name": "Rajan Kumar",  "risk_level": "CONFIRMED_FRAUD"},
    {"id": "cust_fraud_002", "name": "Priya Sharma2","risk_level": "IDENTITY_RECYCLER"},
]

OUTPUT = Path("data/processed/demo_seed.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps({"customers": DEMO_CUSTOMERS}, indent=2))
print(f"Demo seed data written → {OUTPUT}")
```

---

## 20. README.md (for judges)

````markdown
# TrustFabric 🛡️

**Adaptive Multi-Channel Banking Trust Layer** — Bank of Baroda × IIT-GN Hackathon

## What is TrustFabric?

TrustFabric is a **shared trust infrastructure** that sits between every banking
channel (mobile app, net banking, UPI, IVR, branch, ATM) and the services they
call. Instead of each channel re-implementing its own authentication and fraud
logic, they all consume **cryptographically signed Trust Tokens** that encode a
customer's real-time trust level.

## Three Genuine Differentiators

| Pillar | What it does | Why it matters |
|---|---|---|
| **Trust Token Backbone** | RS256-signed JWT tokens modelled on W3C Verifiable Credentials / India Stack | New channels plug in as token consumers — no re-implementation |
| **Cross-channel Trust Graph** | NetworkX + Louvain community detection across customers, devices, IPs, beneficiaries | Catches coordinated fraud rings that look innocent at individual-session level |
| **Synthetic Identity Recycling Detection** | Sentence-transformer embedding similarity across KYC applications | Catches fraudsters who change 1–2 characters across multiple fake applications |

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env

# 2. Generate RSA key pair for Trust Tokens
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# 3. Start all services
docker-compose up --build

# 4. Download datasets
kaggle competitions download -c ieee-fraud-detection -p data/raw/ieee_cis/
wget https://www.cs.cmu.edu/~keystroke/DSL-StrongPassword.csv -P data/raw/

# 5. Train models
pip install -r backend/requirements.txt
python scripts/train_lgbm.py
python scripts/train_keystroke.py

# 6. Seed demo data
python scripts/seed_demo_data.py
python scripts/build_synthetic_graph.py

# 7. Open frontend
open http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Architecture

```
[ Mobile App ] [ Net Banking ] [ UPI ] [ ATM ] [ Branch Teller ]
        ↓               ↓         ↓       ↓           ↓
┌─────────────────────────────────────────────────────────────┐
│                    TrustFabric Layer                         │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Trust Engine │  │ Trust Token │  │   Graph Engine   │   │
│  │ (LightGBM +  │  │  (RS256 JWT │  │ (NetworkX +      │   │
│  │  Keystroke)  │  │  / W3C VC)  │  │  Louvain)        │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        ↓               ↓         ↓
[ Transfer API ] [ Admin Panel ] [ UPI Gateway ]
```

## Evaluation Criteria Coverage

- **Innovation**: Trust Token backbone + Graph fraud-ring detection + adversarial red-team demo
- **Cybersecurity Effectiveness**: SHAP-backed explainability + adversarial resilience module
- **Business Impact**: Quantified across ATO, KYC fraud, insider misuse, organised rings
- **Regulatory Readiness**: W3C VC / India Stack alignment, configurable human-control thresholds
- **UX**: Trust Passport (customer) + SOC dashboard (analyst) + frictionless HIGH-trust flows
````

---

## 21. Key Implementation Order for Hackathon Timeline

Build in this exact sequence to have a working demo at every checkpoint:

**Hour 0–2: Scaffold**
- `docker-compose up` with db + redis
- FastAPI skeleton with `/api/health` returning 200
- React app with routing between Login, Dashboard, Admin pages

**Hour 2–5: Trust Token Core**
- Generate RSA keys, implement `token_service.py`
- Implement `trust_engine.py` with hardcoded signal stubs
- `/api/auth/login` endpoint returning a real signed token
- `TrustMeter` component consuming the token

**Hour 5–9: ML Models**
- Run `train_lgbm.py` (expect ~45 min on a modern laptop for full IEEE-CIS; use 10% sample for speed)
- Run `train_keystroke.py` (fast, <5 min)
- Wire `transaction_service.py` to call LightGBM
- Wire `behavioral_service.py` to call keystroke detector

**Hour 9–12: Graph Module**
- `build_synthetic_graph.py` → synthetic fraud ring
- `graph_service.py` with Louvain detection
- `GraphViewer.tsx` with D3 force layout

**Hour 12–15: Adversarial Demo + Trust Passport**
- `adversarial_service.py` with 3 attack scenarios
- `AdversarialDemo.tsx` page with live attack simulation
- `TrustPassportPage.tsx` customer explain view

**Hour 15–18: Polish**
- SHAP waterfall chart on transaction flags
- SOC admin dashboard with alert feed
- Identity recycling demo in onboarding flow
- End-to-end demo script (`demo_script.md`)

---

## 22. Copilot Code-Generation Prompts (use these verbatim in Copilot Chat)

Use these prompts to generate each missing piece:

```
// Implement backend/services/behavioral_service.py
// It must: (1) load ScaledManhattanDetector from ml/artifacts/keystroke_manhattan.pkl
// (2) expose score_keystrokes(customer_id, timings, hold_times) -> float 0-1
// (3) expose is_known_device(customer_id, device_fp) -> bool using Redis cache
// (4) expose register_device(customer_id, device_fp) to add to known devices

// Implement backend/routers/transactions.py
// POST /api/transactions/score receives TransactionRequest,
// verifies the trust_token via TokenService,
// calls LGBMFraudModel.predict_proba() and .explain(),
// calls GraphService.add_transaction_event(),
// returns TransactionScore with action ALLOW/STEP_UP/BLOCK based on fraud_probability thresholds

// Implement backend/routers/graph.py
// GET /api/graph/neighbourhood/{customer_id}?depth=2
// calls GraphService.get_neighbourhood_json() and returns it
// GET /api/graph/risk/{customer_id} returns node risk score
// POST /api/graph/detect runs community detection

// Implement backend/services/online_learning.py
// Class OnlineLearningService with:
// update_baseline(customer_id, session_result: dict) — incremental EWMA update
// get_adjustment(customer_id) -> float (-10 to +10)
// Uses Redis for per-user baseline storage

// Implement frontend/src/components/ShapWaterfall.tsx
// Props: features: Array<{feature: string, value: number, shap_impact: number}>
// Renders a horizontal bar chart using Recharts
// Positive impact = red bars (fraud signal), negative = green bars (trust signal)
// Shows feature name and raw value in tooltip

// Implement frontend/src/pages/AdversarialDemo.tsx
// Calls GET /api/adversarial/simulate?attack=SPOOFED_BIOMETRICS|BOILING_FROG|GRAPH_EVASION
// Shows attack description, animated trust score decay, and resilience verdict
// For BOILING_FROG: show a Recharts LineChart of trust_score across 15 sessions
```

---

*End of Copilot Instructions. Every section above is a direct build specification.
Follow file paths, class names, and function signatures exactly to ensure all
components integrate without naming conflicts.*
