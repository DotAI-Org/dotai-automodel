"""Run full pipeline on transactions.csv and print all LLM outputs."""
import json
import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Stage 1: Upload
with open("tests/test_data/improvedTransactions.csv", "rb") as f:
    resp = client.post("/sessions", files={"file": ("improvedTransactions.csv", f, "text/csv")})
print("=== STAGE 1: UPLOAD ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
sid = data["session_id"]
print(f"Session ID: {sid}")
print(f"Row count: {data['profile']['row_count']}")
for col in data["profile"]["columns"]:
    print(f"  {col['name']:15s} dtype={col['dtype']:12s} nulls={col['null_count']} uniques={col['unique_count']} samples={col['sample_values'][:3]}")
print()

# Stage 2: Column Mapping (LLM)
resp = client.post(f"/sessions/{sid}/column-mapping")
print("=== STAGE 2: COLUMN MAPPING (LLM OUTPUT) ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
for col in data["columns"]:
    print(f"  {col['name']:15s} -> {col['llm_role']:20s} (confidence: {col['confidence']})")
print()

# Stage 3: Hypothesis (LLM)
resp = client.post(f"/sessions/{sid}/hypothesis")
print("=== STAGE 3: HYPOTHESIS (LLM OUTPUT) ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
h = data["hypothesis"]
print(f"  Business type: {h['type']}")
print(f"  Confidence: {h['confidence']}")
print(f"  Reasoning: {h['reasoning']}")
print()
print(f"  Questions ({len(data['questions'])}):")
for q in data["questions"]:
    options = ", ".join(o["label"] for o in q["options"])
    print(f"    - {q['question']}")
    print(f"      Options: [{options}]")
print()

# Stage 4: Features (LLM selects Tier 2)
resp = client.post(f"/sessions/{sid}/features", json={"answers": {}})
print("=== STAGE 4: FEATURES (LLM SELECTED TIER 2) ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
print(f"  Feature count: {data['feature_count']}")
print(f"  User count: {data['user_count']}")
print(f"  Tier 1: {data['feature_tiers']['tier1']}")
print(f"  Tier 2: {data['feature_tiers']['tier2']}")
print(f"  Stats:")
for s in data["stats"]:
    mean_str = str(s["mean"]) if s["mean"] is not None else "N/A"
    median_str = str(s["median"]) if s["median"] is not None else "N/A"
    print(f"    {s['name']:35s} mean={mean_str:>10s}  median={median_str:>10s}  null%={s['null_pct']}")
print()

# Stage 5: Labels
resp = client.post(f"/sessions/{sid}/labels")
print("=== STAGE 5: LABELS ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
print(f"  Churn window: {data['churn_window_days']} days")
print(f"  Cutoff date: {data['cutoff_date']}")
print(f"  Churn rate: {data['churn_rate']*100:.1f}%")
print(f"  Churned: {data['churned_count']}, Active: {data['active_count']}")
print()

# Stage 6: Train
resp = client.post(f"/sessions/{sid}/train")
print("=== STAGE 6: TRAIN ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
for k, v in data["metrics"].items():
    print(f"  {k}: {v}")
cm = data["confusion_matrix"]
print(f"  Confusion matrix: TP={cm['true_positive']} FP={cm['false_positive']} TN={cm['true_negative']} FN={cm['false_negative']}")
print(f"  Feature importance:")
for fi in data["feature_importance"]:
    print(f"    {fi['feature']:35s} {fi['importance']}")
print(f"  Training time: {data['training_time_seconds']}s")
print()

# Stage 7: Results (LLM summary)
resp = client.get(f"/sessions/{sid}/results")
print("=== STAGE 7: RESULTS SUMMARY (LLM OUTPUT) ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
print(f"  {data['summary']}")
print()

# Stage 8: Inference
resp = client.post(f"/sessions/{sid}/inference")
print("=== STAGE 8: INFERENCE ===")
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()}")
    sys.exit(1)
data = resp.json()
print(f"  Total: {data['total_users']}")
print(f"  High risk: {data['high_risk_count']}")
print(f"  Medium risk: {data['medium_risk_count']}")
print(f"  Low risk: {data['low_risk_count']}")
print()
print("  Top 5 high-risk:")
high = sorted([p for p in data["predictions"] if p["risk_tier"] == "High"], key=lambda x: -x["churn_probability"])
for p in high[:5]:
    feats = ", ".join(f"{f['feature']} ({f['contribution']:+.4f})" for f in p["top_features"])
    print(f"    {p['customer_id']}: {p['churn_probability']*100:.1f}% | {feats}")
print()
print("  Top 5 low-risk:")
low = sorted([p for p in data["predictions"] if p["risk_tier"] == "Low"], key=lambda x: x["churn_probability"])
for p in low[:5]:
    feats = ", ".join(f"{f['feature']} ({f['contribution']:+.4f})" for f in p["top_features"])
    print(f"    {p['customer_id']}: {p['churn_probability']*100:.1f}% | {feats}")
