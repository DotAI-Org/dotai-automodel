"""End-to-end pipeline test using sample CSV and real Gemini API."""

import os
import sys
import requests
import json
import time

BASE_URL = os.environ.get("CHURN_TOOL_URL", "http://localhost:8000")


def test_pipeline():
    csv_path = os.path.join(os.path.dirname(__file__), "test_data", "ecommerce_sample.csv")
    if not os.path.exists(csv_path):
        print(f"Test CSV not found at {csv_path}. Run generate_test_data.py first.")
        sys.exit(1)

    # Stage 1: Upload
    print("=== Stage 1: Upload ===")
    with open(csv_path, "rb") as f:
        resp = requests.post(f"{BASE_URL}/sessions", files={"file": ("test.csv", f, "text/csv")})
    assert resp.status_code == 200, f"Upload failed: {resp.text}"
    data = resp.json()
    session_id = data["session_id"]
    profile = data["profile"]
    print(f"Session: {session_id}")
    print(f"Rows: {profile['row_count']}, Columns: {len(profile['columns'])}")
    print(f"Date range: {profile.get('date_range')}")
    print()

    # Stage 2: Column Mapping
    print("=== Stage 2: Column Mapping ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/column-mapping")
    assert resp.status_code == 200, f"Column mapping failed: {resp.text}"
    data = resp.json()
    for col in data["columns"]:
        print(f"  {col['name']}: {col['llm_role']} (confidence: {col['confidence']})")
    print()

    # Stage 3: Hypothesis
    print("=== Stage 3: Hypothesis ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/hypothesis")
    assert resp.status_code == 200, f"Hypothesis failed: {resp.text}"
    data = resp.json()
    print(f"Business type: {data['hypothesis']['type']} (confidence: {data['hypothesis']['confidence']})")
    print(f"Questions: {len(data['questions'])}")
    for q in data["questions"]:
        print(f"  [{q['id']}] {q['question']}")
        for opt in q["options"]:
            print(f"    - {opt['label']} ({opt['value']})")
    print()

    # Stage 4: Features (answer MCQs with first option)
    print("=== Stage 4: Features ===")
    answers = {}
    for q in data["questions"]:
        answers[q["id"]] = q["options"][0]["value"]
    print(f"Answering with first options: {answers}")

    resp = requests.post(
        f"{BASE_URL}/sessions/{session_id}/features",
        json={"answers": answers},
    )
    assert resp.status_code == 200, f"Features failed: {resp.text}"
    data = resp.json()
    print(f"Users: {data['user_count']}, Features: {data['feature_count']}")
    print(f"Tier 1: {data['feature_tiers']['tier1']}")
    print(f"Tier 2: {data['feature_tiers']['tier2']}")
    print()

    # Stage 5: Labels
    print("=== Stage 5: Labels ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/labels")
    assert resp.status_code == 200, f"Labels failed: {resp.text}"
    data = resp.json()
    print(f"Churn rate: {data['churn_rate']}")
    print(f"Churned: {data['churned_count']}, Active: {data['active_count']}")
    print(f"Window: {data['churn_window_days']} days, Cutoff: {data['cutoff_date']}")
    print()

    # Stage 6: Train
    print("=== Stage 6: Train ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/train")
    assert resp.status_code == 200, f"Train failed: {resp.text}"
    data = resp.json()
    print(f"AUC: {data['metrics']['auc']}")
    print(f"Precision: {data['metrics']['precision']}")
    print(f"Recall: {data['metrics']['recall']}")
    print(f"F1: {data['metrics']['f1']}")
    print(f"Training time: {data['training_time_seconds']}s")
    print(f"Top features: {[fi['feature'] for fi in data['feature_importance'][:5]]}")
    print()

    # Stage 7: Results
    print("=== Stage 7: Results ===")
    resp = requests.get(f"{BASE_URL}/sessions/{session_id}/results")
    assert resp.status_code == 200, f"Results failed: {resp.text}"
    data = resp.json()
    print(f"Summary: {data['summary'][:200]}...")
    print(f"Sample predictions: {len(data['sample_predictions'])}")
    print()

    # Stage 8: Inference
    print("=== Stage 8: Inference ===")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/inference")
    assert resp.status_code == 200, f"Inference failed: {resp.text}"
    data = resp.json()
    print(f"Total users: {data['total_users']}")
    print(f"High risk: {data['high_risk_count']}")
    print(f"Medium risk: {data['medium_risk_count']}")
    print(f"Low risk: {data['low_risk_count']}")
    print()

    # Download CSV
    print("=== Download CSV ===")
    resp = requests.get(f"{BASE_URL}/sessions/{session_id}/inference/download")
    assert resp.status_code == 200, f"Download failed: {resp.text}"
    print(f"CSV size: {len(resp.text)} bytes")
    lines = resp.text.strip().split("\n")
    print(f"CSV rows: {len(lines) - 1}")
    print(f"Header: {lines[0]}")
    print(f"First row: {lines[1]}")
    print()

    print("=== ALL STAGES PASSED ===")


if __name__ == "__main__":
    test_pipeline()
