import json
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parents[1]
    output_path = root_dir / "data" / "processed" / "demo_seed.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    DEMO_CUSTOMERS = [
        {"id": "cust_001", "name": "Priya Sharma",       "risk_level": "LOW"},
        {"id": "cust_002", "name": "Arjun Patel",        "risk_level": "LOW"},
        {"id": "cust_003", "name": "Kavita Nair",        "risk_level": "MEDIUM"},
        {"id": "cust_004", "name": "Rohit Mehta",        "risk_level": "HIGH"},
        {"id": "cust_005", "name": "Sunita Joshi",       "risk_level": "LOW"},
        {"id": "cust_fraud_001", "name": "Rajan Kumar",  "risk_level": "CONFIRMED_FRAUD"},
        {"id": "cust_fraud_002", "name": "Priya Sharma2","risk_level": "IDENTITY_RECYCLER"},
    ]

    output_path.write_text(json.dumps({"customers": DEMO_CUSTOMERS}, indent=2))
    print(f"Demo seed data written -> {output_path}")

if __name__ == "__main__":
    main()
