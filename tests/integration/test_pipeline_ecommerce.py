import os
import io
import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.llm, pytest.mark.slow]

BASE_URL = os.environ.get("CHURN_TOOL_URL", "")


@pytest.fixture(scope="module")
def pipeline_state():
    """Run stages 1-8 once, share state across tests."""
    if BASE_URL:
        import requests
        session = {"base_url": BASE_URL, "use_requests": True}
    else:
        from app.main import app
        session = {"client": TestClient(app), "use_requests": False}

    state = {}

    # Stage 1: Upload
    csv_path = os.path.join(os.path.dirname(__file__), "..", "test_data", "ecommerce_sample.csv")
    with open(csv_path, "rb") as f:
        if session.get("use_requests"):
            import requests
            resp = requests.post(f"{BASE_URL}/sessions", files={"file": ("ecommerce_sample.csv", f, "text/csv")})
        else:
            resp = session["client"].post("/sessions", files={"file": ("ecommerce_sample.csv", f, "text/csv")})

    state["upload"] = resp
    assert resp.status_code == 200
    data = resp.json()
    sid = data["session_id"]
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

    # Stage 2: Column mapping
    resp = _post(f"/sessions/{sid}/column-mapping")
    state["column_mapping"] = resp
    assert resp.status_code == 200

    # Stage 3: Hypothesis
    resp = _post(f"/sessions/{sid}/hypothesis")
    state["hypothesis"] = resp
    assert resp.status_code == 200

    # Stage 4: Features
    resp = _post(f"/sessions/{sid}/features", json={"answers": {}})
    state["features"] = resp
    assert resp.status_code == 200

    # Stage 5: Labels
    resp = _post(f"/sessions/{sid}/labels")
    state["labels"] = resp
    assert resp.status_code == 200

    # Stage 6: Train
    resp = _post(f"/sessions/{sid}/train")
    state["train"] = resp
    assert resp.status_code == 200

    # Stage 7: Results
    resp = _get(f"/sessions/{sid}/results")
    state["results"] = resp
    assert resp.status_code == 200

    # Stage 8: Inference
    resp = _post(f"/sessions/{sid}/inference")
    state["inference"] = resp
    assert resp.status_code == 200

    # Download
    resp = _get(f"/sessions/{sid}/inference/download")
    state["download"] = resp
    assert resp.status_code == 200

    return state


class TestUpload:
    def test_status_and_profile(self, pipeline_state):
        data = pipeline_state["upload"].json()
        assert data["profile"]["row_count"] == 5000
        assert len(data["profile"]["columns"]) == 8


class TestColumnMapping:
    def test_mapping_confidence(self, pipeline_state):
        data = pipeline_state["column_mapping"].json()
        cols = data["columns"]
        mapped = {c["llm_role"]: c for c in cols if c["llm_role"] != "other"}
        assert "customer_id" in mapped
        assert "transaction_date" in mapped
        assert "amount" in mapped
        for role in ["customer_id", "transaction_date", "amount"]:
            assert mapped[role]["confidence"] > 0.7


class TestHypothesis:
    def test_questions_returned(self, pipeline_state):
        data = pipeline_state["hypothesis"].json()
        questions = data["questions"]
        assert 4 <= len(questions) <= 8
        btype = data["hypothesis"]["type"].lower()
        assert any(kw in btype for kw in ["commerce", "retail", "e-commerce", "ecommerce", "shop", "store", "sales", "business"])


class TestFeatures:
    def test_feature_count_and_users(self, pipeline_state):
        data = pipeline_state["features"].json()
        assert data["feature_count"] >= 10
        assert data["user_count"] == 200


class TestLabels:
    def test_churn_rate_range(self, pipeline_state):
        data = pipeline_state["labels"].json()
        assert 0.1 <= data["churn_rate"] <= 0.6


class TestTrain:
    def test_quality_metrics(self, pipeline_state):
        data = pipeline_state["train"].json()
        assert data["metrics"]["auc"] >= 0.65
        assert data["metrics"]["f1"] >= 0.3


class TestResults:
    def test_summary_present(self, pipeline_state):
        data = pipeline_state["results"].json()
        assert len(data["summary"]) > 0
        assert len(data["sample_predictions"]) > 0


class TestInference:
    def test_tier_distribution(self, pipeline_state):
        data = pipeline_state["inference"].json()
        assert data["high_risk_count"] >= 1
        assert data["low_risk_count"] >= 1
        assert data["high_risk_count"] + data["medium_risk_count"] + data["low_risk_count"] == data["total_users"]
        assert data["total_users"] == 200


class TestDownload:
    def test_csv_row_count(self, pipeline_state):
        content = pipeline_state["download"].text
        lines = content.strip().split("\n")
        assert len(lines) == 201  # header + 200 data rows
