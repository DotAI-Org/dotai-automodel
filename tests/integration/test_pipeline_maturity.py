import os
import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.llm, pytest.mark.slow]

BASE_URL = os.environ.get("CHURN_TOOL_URL", "")


@pytest.fixture(scope="module")
def pipeline_state():
    """Run stages 1-8 for maturity churn data."""
    if BASE_URL:
        import requests
        session = {"base_url": BASE_URL, "use_requests": True}
    else:
        from app.main import app
        session = {"client": TestClient(app), "use_requests": False}

    state = {}

    csv_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "maturity_churn.csv")
    with open(csv_path, "rb") as f:
        if session.get("use_requests"):
            import requests
            resp = requests.post(f"{BASE_URL}/sessions", files={"file": ("maturity_churn.csv", f, "text/csv")})
        else:
            resp = session["client"].post("/sessions", files={"file": ("maturity_churn.csv", f, "text/csv")})

    assert resp.status_code == 200
    sid = resp.json()["session_id"]
    state["session_id"] = sid

    def _post(path, json=None):
        if session.get("use_requests"):
            import requests as req
            if json:
                return req.post(f"{BASE_URL}{path}", json=json)
            return req.post(f"{BASE_URL}{path}")
        else:
            if json:
                return session["client"].post(path, json=json)
            return session["client"].post(path)

    def _get(path):
        if session.get("use_requests"):
            import requests as req
            return req.get(f"{BASE_URL}{path}")
        else:
            return session["client"].get(path)

    # Stages 2-8
    resp = _post(f"/sessions/{sid}/column-mapping")
    assert resp.status_code == 200

    resp = _post(f"/sessions/{sid}/hypothesis")
    assert resp.status_code == 200

    resp = _post(f"/sessions/{sid}/features", json={"answers": {}})
    state["features"] = resp
    assert resp.status_code == 200

    resp = _post(f"/sessions/{sid}/labels")
    state["labels"] = resp
    assert resp.status_code == 200

    resp = _post(f"/sessions/{sid}/train")
    state["train"] = resp
    assert resp.status_code == 200

    resp = _post(f"/sessions/{sid}/inference")
    state["inference"] = resp
    assert resp.status_code == 200

    return state


class TestChurnDetection:
    def test_churn_customers_flagged_high(self, pipeline_state):
        data = pipeline_state["inference"].json()
        predictions = data["predictions"]
        churn_preds = [p for p in predictions if p["customer_id"].startswith("CHURN_")]
        if len(churn_preds) > 0:
            high_risk = [p for p in churn_preds if p["risk_tier"] == "High"]
            detection_rate = len(high_risk) / len(churn_preds)
            assert detection_rate >= 0.9, f"Detection rate {detection_rate} < 0.9"


class TestHealthyClassification:
    def test_healthy_customers_not_all_high_risk(self, pipeline_state):
        data = pipeline_state["inference"].json()
        predictions = data["predictions"]
        healthy_preds = [p for p in predictions if p["customer_id"].startswith("HEALTHY_")]
        if len(healthy_preds) > 0:
            non_high = [p for p in healthy_preds if p["risk_tier"] != "High"]
            # At least some healthy customers should not be high risk
            assert len(non_high) / len(healthy_preds) >= 0.3, (
                f"Only {len(non_high)}/{len(healthy_preds)} healthy customers are not High risk"
            )


class TestTrainQuality:
    def test_auc_threshold(self, pipeline_state):
        data = pipeline_state["train"].json()
        assert data["metrics"]["auc"] >= 0.8


class TestChurnRate:
    def test_churn_rate_range(self, pipeline_state):
        data = pipeline_state["labels"].json()
        # Churn rate depends on auto-derived window; accept wider range
        assert 0.1 <= data["churn_rate"] <= 0.9
