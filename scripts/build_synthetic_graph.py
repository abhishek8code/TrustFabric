import random
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.services.graph_service import GraphService

def main():
    root_dir = Path(__file__).resolve().parents[1]
    output_path = root_dir / "data" / "processed" / "synthetic_graph.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    # Mark orchestrator as confirmed fraud and run community detection
    gs.mark_confirmed_fraud(orchestrator)
    gs.run_community_detection()

    # Export ego graph of orchestrator
    graph_data = gs.get_neighbourhood_json(orchestrator, depth=3)
    output_path.write_text(json.dumps(graph_data, indent=2))
    print(f"Synthetic graph written -> {output_path}")
    print(f"  Nodes: {len(graph_data['nodes'])}, Links: {len(graph_data['links'])}")

if __name__ == "__main__":
    main()
