import pytest
import pandas as pd
import numpy as np
from fastapi import HTTPException

from app.stages.s5_labels import _get_churn_window, handle
from app.session_store import store, SessionStore
from app.stages.s4_features import TIER1_FEATURES
from tests.conftest import _create_test_session


def _make_df(rows):
    return pd.DataFrame(rows, columns=["customer_id", "transaction_date", "amount"])


COL_MAP = {
    "customer_id": "customer_id",
    "transaction_date": "transaction_date",
    "amount": "amount",
}


class TestGetChurnWindow:
    def test_mcq_churn_window_key(self):
        df = _make_df([("A", "2024-01-01", 10)])
        result = _get_churn_window(df, COL_MAP, {"churn_window": "60"})
        assert result == 60

    def test_mcq_inactive_days_key(self):
        df = _make_df([("A", "2024-01-01", 10)])
        result = _get_churn_window(df, COL_MAP, {"inactive_days_threshold": "30"})
        assert result == 30

    def test_no_mcq_auto_derives(self):
        # Customers with 30-day gaps -> median gap 30 -> churn window = 60
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-31", 20),
            ("A", "2024-03-01", 30),
            ("B", "2024-01-01", 10),
            ("B", "2024-01-31", 20),
            ("B", "2024-03-01", 30),
        ])
        result = _get_churn_window(df, COL_MAP, {})
        assert result == 60

    def test_computed_below_14_clamped(self):
        # Very small gaps -> 2x median < 14 -> clamped to 14
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-04", 20),  # 3-day gap
            ("A", "2024-01-07", 30),  # 3-day gap
            ("B", "2024-01-01", 10),
            ("B", "2024-01-04", 20),
            ("B", "2024-01-07", 30),
        ])
        result = _get_churn_window(df, COL_MAP, {})
        # 2x median(3) = 6, clamped to 14
        assert result == 14

    def test_computed_above_365_clamped(self):
        # Large gaps -> 2x median > 365 -> clamped to 365
        df = _make_df([
            ("A", "2020-01-01", 10),
            ("A", "2021-01-01", 20),  # 366-day gap
            ("B", "2020-01-01", 10),
            ("B", "2021-01-01", 20),
        ])
        result = _get_churn_window(df, COL_MAP, {})
        assert result == 365

    def test_all_single_txn_fallback_90(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("B", "2024-02-01", 20),
            ("C", "2024-03-01", 30),
        ])
        result = _get_churn_window(df, COL_MAP, {})
        assert result == 90


class TestHandle:
    def _build_session(self, df, col_map, mcq_answers=None):
        """Use the module-level store so handle() can update it."""
        sid = _create_test_session(store)
        feature_matrix = pd.DataFrame()
        for name, func in TIER1_FEATURES.items():
            try:
                feature_matrix[name] = func(df, col_map)
            except Exception:
                continue
        store.update(sid, {
            "dataframe": df,
            "col_map": col_map,
            "feature_matrix": feature_matrix,
            "mcq_answers": mcq_answers or {},
        })
        return sid

    def test_known_churners_labeled_1(self):
        # A buys only in Jan, B buys through June
        # With churn_window=30, cutoff ~ June 1
        # A has no txns after cutoff -> churn=1
        # B has txns after cutoff -> churn=0
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-15", 20),
            ("A", "2024-02-01", 30),
            ("B", "2024-01-01", 10),
            ("B", "2024-03-01", 20),
            ("B", "2024-05-01", 30),
            ("B", "2024-06-15", 40),
            ("B", "2024-06-30", 50),
        ])
        sid = self._build_session(df, COL_MAP, {"churn_window": "30"})
        session = store.get(sid)
        handle(sid, session)
        session = store.get(sid)
        labels = session["labels"]
        assert labels["A"] == 1
        assert labels["B"] == 0

    def test_churn_rate_computed(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-15", 20),
            ("B", "2024-01-01", 10),
            ("B", "2024-03-01", 20),
            ("B", "2024-05-01", 30),
            ("B", "2024-06-30", 40),
        ])
        sid = self._build_session(df, COL_MAP, {"churn_window": "30"})
        session = store.get(sid)
        result = handle(sid, session)
        assert 0.0 <= result["churn_rate"] <= 1.0
        assert result["churned_count"] + result["active_count"] > 0

    def test_raises_400_when_feature_matrix_missing(self):
        sid = _create_test_session(store)
        store.update(sid, {
            "dataframe": _make_df([("A", "2024-01-01", 10)]),
            "col_map": COL_MAP,
            "feature_matrix": None,
            "mcq_answers": {},
        })
        session = store.get(sid)
        with pytest.raises(HTTPException) as exc_info:
            handle(sid, session)
        assert exc_info.value.status_code == 400

    def test_churn_window_stored_in_session(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-02-01", 20),
            ("B", "2024-01-01", 10),
            ("B", "2024-03-01", 20),
            ("B", "2024-05-01", 30),
            ("B", "2024-06-30", 40),
        ])
        sid = self._build_session(df, COL_MAP, {"churn_window": "45"})
        session = store.get(sid)
        handle(sid, session)
        session = store.get(sid)
        assert session["churn_window_days"] == 45
