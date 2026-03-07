import pytest
import io
import pandas as pd
import numpy as np
from fastapi import HTTPException

from app.stages.s4_features import TIER1_FEATURES
from app.stages import s5_labels, s6_train, s8_inference
from app.stages.s4_features import (
    compute_recency,
    compute_days_between_purchases_avg,
    compute_monetary_total,
    compute_monetary_avg,
)
from app.session_store import store, SessionStore

from tests.generators.generate_edge_case_data import (
    make_empty_df,
    make_single_customer,
    make_all_churned,
    make_all_active,
    make_single_day,
    make_negative_amounts,
)

COL_MAP = {
    "customer_id": "customer_id",
    "transaction_date": "transaction_date",
    "amount": "amount",
}


def _compute_features(df, col_map):
    feature_matrix = pd.DataFrame()
    for name, func in TIER1_FEATURES.items():
        try:
            feature_matrix[name] = func(df, col_map)
        except Exception:
            continue
    return feature_matrix


def _build_session_through_labels(df, col_map, mcq_answers=None):
    """Use module-level store so handle() can update it."""
    sid = store.create()
    feature_matrix = _compute_features(df, col_map)
    store.update(sid, {
        "dataframe": df,
        "col_map": col_map,
        "feature_matrix": feature_matrix,
        "mcq_answers": mcq_answers or {},
    })
    session = store.get(sid)
    return sid, session, store


class TestEmptyCSV:
    def test_empty_df_features_empty(self):
        df = make_empty_df()
        fm = _compute_features(df, COL_MAP)
        assert len(fm) == 0


class TestSingleCustomer:
    def test_single_customer_label_raises_or_handles(self):
        df = make_single_customer(n_txns=5)
        sid, session, store = _build_session_through_labels(df, COL_MAP)
        # s5 should work but s6 will fail on stratify with single class
        result = s5_labels.handle(sid, session)
        session = store.get(sid)
        # Training should raise 400 because stratified split needs >=2 per class
        with pytest.raises((HTTPException, ValueError)):
            s6_train.handle(sid, session)


class TestAllChurned:
    def test_all_churned_train_raises(self):
        df = make_all_churned(n=50)
        sid, session, store = _build_session_through_labels(
            df, COL_MAP, {"churn_window": "90"}
        )
        result = s5_labels.handle(sid, session)
        session = store.get(sid)
        labels = session.get("labels")
        if labels is not None and labels.nunique() == 1:
            with pytest.raises((HTTPException, ValueError)):
                s6_train.handle(sid, session)


class TestAllActive:
    def test_all_active_train_raises(self):
        df = make_all_active(n=50)
        sid, session, store = _build_session_through_labels(
            df, COL_MAP, {"churn_window": "14"}
        )
        result = s5_labels.handle(sid, session)
        session = store.get(sid)
        labels = session.get("labels")
        if labels is not None and labels.nunique() == 1:
            with pytest.raises((HTTPException, ValueError)):
                s6_train.handle(sid, session)


class TestSingleDay:
    def test_single_day_no_crash(self):
        df = make_single_day(n=20)
        result = compute_days_between_purchases_avg(df, COL_MAP)
        # All single-txn customers -> all NaN
        assert result.isna().all()

    def test_single_day_recency_zero(self):
        df = make_single_day(n=20)
        result = compute_recency(df, COL_MAP)
        assert (result == 0).all()


class TestNegativeAmounts:
    def test_no_crash_in_monetary(self):
        df = make_negative_amounts(n=20)
        total = compute_monetary_total(df, COL_MAP)
        avg = compute_monetary_avg(df, COL_MAP)
        assert len(total) > 0
        assert len(avg) > 0


class TestNonCSVUpload:
    def test_rejects_non_csv(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        content = b"not,a,csv\ndata"
        response = client.post(
            "/sessions",
            files={"file": ("data.txt", io.BytesIO(content), "text/plain")},
        )
        assert response.status_code == 400


class TestInvalidSessionId:
    def test_404_on_labels(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post("/sessions/nonexistent123/labels")
        assert response.status_code == 404


class TestStageOutOfOrder:
    def test_features_before_hypothesis_raises_400(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        # Upload a CSV first
        df = make_negative_amounts(n=10)
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        resp = client.post(
            "/sessions",
            files={"file": ("test.csv", io.BytesIO(buf.getvalue().encode()), "text/csv")},
        )
        assert resp.status_code == 200
        sid = resp.json()["session_id"]
        # Try features (stage 4) without hypothesis (stage 3)
        resp = client.post(
            f"/sessions/{sid}/features",
            json={"answers": {}},
        )
        assert resp.status_code == 400
