from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import admin, adversarial, auth, graph, onboarding, transactions, trust_passport


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.ml.lgbm_model import LGBMFraudModel
    from backend.ml.keystroke_model import ScaledManhattanDetector
    from backend.services.graph_service import GraphService
    from backend.services.identity_service import IdentityService

    app.state.lgbm = LGBMFraudModel(settings.LGBM_MODEL_PATH)
    app.state.keystroke = ScaledManhattanDetector()
    app.state.identity = IdentityService()
    app.state.graph = GraphService()
    print("[OK] Models loaded")
    yield


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

app.include_router(auth.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(trust_passport.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(adversarial.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "TrustFabric"}
