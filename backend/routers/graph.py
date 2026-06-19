from __future__ import annotations

from fastapi import APIRouter

from backend.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Graph"])
graph_svc = GraphService()


@router.get("/neighbourhood/{customer_id}")
async def neighbourhood(customer_id: str, depth: int = 2):
    return graph_svc.get_neighbourhood_json(customer_id, depth=depth)


@router.get("/risk/{customer_id}")
async def risk(customer_id: str):
    return {"customer_id": customer_id, "risk": graph_svc.get_node_risk(customer_id)}


@router.post("/detect")
async def detect():
    graph_svc.run_community_detection()
    return {"status": "ok"}
