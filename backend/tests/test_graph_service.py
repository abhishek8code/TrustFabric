from backend.services.graph_service import GraphService


def test_graph_service_builds_neighbourhood():
    svc = GraphService()
    svc.add_login_event("cust_001", "device-a", "10.0.0.1", "session-1")
    svc.add_transaction_event("cust_001", "beneficiary-a", 1000, "tx-1")
    data = svc.get_neighbourhood_json("cust_001", depth=2)
    assert data["nodes"]
    assert data["links"]
