"""Test pipeline accuracy for maturity-based churn data."""

import os
import sys
import requests
import json

BASE_URL = os.environ.get("CHURN_TOOL_URL", "http://localhost:8000")

def run_maturity_test():
    csv_path = "tests/test_data/maturity_churn.csv"
    if not os.path.exists(csv_path):
        print("CSV not found. Run generate_maturity_churn_data.py first.")
        sys.exit(1)

    print("=== Stage 1: Upload ===")
    with open(csv_path, "rb") as f:
        resp = requests.post(f"{BASE_URL}/sessions", files={"file": ("maturity_churn.csv", f, "text/csv")})
    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    session_id = resp.json()["session_id"]
    print(f"Session created: {session_id}")

    print("=== Stage 2: Column Mapping ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/column-mapping")
    assert resp.status_code == 200, resp.text
    print("Mapping complete.")

    print("=== Stage 3: Hypothesis ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/hypothesis")
    assert resp.status_code == 200, resp.text
    hypothesis_data = resp.json()
    print(f"Hypothesis: {hypothesis_data['hypothesis']['type']}")

    print("=== Stage 4: Features ===")
    # Answer questions automatically
    answers = {q["id"]: q["options"][0]["value"] for q in hypothesis_data["questions"]}
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/features", json={"answers": answers})
    assert resp.status_code == 200, resp.text
    print("Features engineered.")

    print("=== Stage 5: Labels ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/labels")
    assert resp.status_code == 200, resp.text
    label_data = resp.json()
    print(f"Churn rate: {label_data['churn_rate']}")

    print("=== Stage 6: Train ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/train")
    assert resp.status_code == 200, resp.text
    train_data = resp.json()
    auc = train_data['metrics']['auc']
    print(f"Model AUC: {auc}")
    assert auc > 0.8, f"AUC too low: {auc}"

    print("=== Stage 8: Inference ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/inference")
    assert resp.status_code == 200, resp.text
    inf_data = resp.json()
    
    churn_users_flagged = 0
    total_churn_users = 100
    for pred in inf_data["predictions"]:
        if pred["customer_id"].startswith("CHURN_"):
            if pred["risk_tier"] == "High":
                churn_users_flagged += 1
    
    flag_rate = churn_users_flagged / total_churn_users
    print(f"Flagged {churn_users_flagged} out of {total_churn_users} churn cohort users ({flag_rate:.1%})")
    assert flag_rate >= 0.9, f"Only flagged {flag_rate:.1%}"

    print("\n=== SUCCESS: MATURITY CHURN DETECTED ===")

if __name__ == "__main__":
    run_maturity_test()
