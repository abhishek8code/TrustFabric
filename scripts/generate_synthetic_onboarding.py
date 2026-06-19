import json
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parents[1]
    output_path = root_dir / "data" / "processed" / "synthetic_onboardings.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ONBOARDINGS = [
        {"application_id": "APP-11111", "full_name": "Priya Sharma", "dob": "1994-05-12", "mobile_last4": "9876", "pincode": "382355", "email_domain": "gmail.com"},
        {"application_id": "APP-22222", "full_name": "Priya Sharma2", "dob": "1994-05-12", "mobile_last4": "9876", "pincode": "382355", "email_domain": "gmail.com"},
        {"application_id": "APP-33333", "full_name": "Arjun Patel", "dob": "1992-08-24", "mobile_last4": "8765", "pincode": "380009", "email_domain": "yahoo.com"},
    ]

    output_path.write_text(json.dumps(ONBOARDINGS, indent=2))
    print(f"Synthetic onboarding data written to {output_path}")

if __name__ == "__main__":
    main()
