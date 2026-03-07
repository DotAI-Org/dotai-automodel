import pytest
import pandas as pd
import numpy as np
from fastapi import HTTPException

from app.stages.s8_inference import handle, handle_download
from app.session_store import store, SessionStore


class TestInferenceHandle:
    def test_total_users_matches_feature_matrix(self, trained_session):
        session, sid, store = trained_session
        feature_matrix = session["feature_matrix"]
        result = handle(sid, session)
        assert result.total_users == len(feature_matrix)

    def test_tier_counts_sum_to_total(self, trained_session):
        session, sid, store = trained_session
        result = handle(sid, session)
        assert result.high_risk_count + result.medium_risk_count + result.low_risk_count == result.total_users

    def test_each_prediction_has_3_top_features(self, trained_session):
        session, sid, store = trained_session
        result = handle(sid, session)
        for pred in result.predictions:
            assert len(pred.top_features) == 3

    def test_probabilities_in_valid_range(self, trained_session):
        session, sid, store = trained_session
        result = handle(sid, session)
        for pred in result.predictions:
            assert 0.0 <= pred.churn_probability <= 1.0

    def test_predictions_stored_in_session(self, trained_session):
        session, sid, store = trained_session
        handle(sid, session)
        updated = store.get(sid)
        assert updated["predictions"] is not None
        assert len(updated["predictions"]) > 0

    def test_raises_400_when_model_missing(self):
        sid = store.create()
        store.update(sid, {
            "model": None,
            "feature_matrix": pd.DataFrame({"f1": [1, 2]}),
            "feature_names": ["f1"],
        })
        session = store.get(sid)
        with pytest.raises(HTTPException) as exc_info:
            handle(sid, session)
        assert exc_info.value.status_code == 400


class TestInferenceDownload:
    def test_csv_columns_and_row_count(self, trained_session):
        session, sid, store = trained_session
        handle(sid, session)
        updated = store.get(sid)
        buffer = handle_download(sid, updated)
        content = buffer.getvalue()
        lines = content.strip().split("\n")
        header = lines[0]
        assert "customer_id" in header
        assert "churn_probability" in header
        assert "risk_tier" in header
        assert "top_feature_contributions" in header
        # data rows = total users in feature matrix
        data_rows = len(lines) - 1
        assert data_rows == len(session["feature_matrix"])

    def test_raises_400_when_predictions_missing(self):
        sid = store.create()
        store.update(sid, {"predictions": None})
        session = store.get(sid)
        with pytest.raises(HTTPException) as exc_info:
            handle_download(sid, session)
        assert exc_info.value.status_code == 400
