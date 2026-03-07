import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.stages.s4_features import (
    compute_recency,
    compute_frequency_30d,
    compute_frequency_60d,
    compute_frequency_90d,
    compute_monetary_total,
    compute_monetary_avg,
    compute_frequency_trend,
    compute_monetary_trend,
    compute_days_between_purchases_avg,
    compute_days_between_purchases_std,
)

COL_MAP = {
    "customer_id": "cid",
    "transaction_date": "date",
    "amount": "amt",
}


def _make_df(rows):
    """Build a DataFrame from list of (customer_id, date_str, amount) tuples."""
    return pd.DataFrame(rows, columns=["cid", "date", "amt"])


class TestComputeRecency:
    def test_last_purchase_10_days_ago(self):
        today = datetime(2024, 6, 15)
        df = _make_df([
            ("A", "2024-06-05", 100),
            ("A", "2024-06-01", 50),
            ("B", "2024-06-15", 200),
        ])
        result = compute_recency(df, COL_MAP)
        assert result["A"] == 10
        assert result["B"] == 0

    def test_same_day_purchase(self):
        df = _make_df([
            ("A", "2024-06-15", 100),
            ("B", "2024-06-15", 200),
        ])
        result = compute_recency(df, COL_MAP)
        assert result["A"] == 0
        assert result["B"] == 0


class TestComputeFrequency30d:
    def test_three_txns_in_window(self):
        base = datetime(2024, 6, 30)
        df = _make_df([
            ("A", "2024-06-05", 10),
            ("A", "2024-06-15", 20),
            ("A", "2024-06-25", 30),
            ("A", "2024-05-01", 40),  # outside 30d window
            ("B", "2024-06-30", 50),
        ])
        result = compute_frequency_30d(df, COL_MAP)
        assert result["A"] == 3
        assert result["B"] == 1

    def test_no_txns_in_window(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("B", "2024-06-30", 50),
        ])
        result = compute_frequency_30d(df, COL_MAP)
        assert result["A"] == 0


class TestComputeFrequency60d:
    def test_count_in_60d(self):
        df = _make_df([
            ("A", "2024-06-30", 10),
            ("A", "2024-06-01", 20),
            ("A", "2024-05-15", 30),
            ("A", "2024-03-01", 40),  # outside 60d
        ])
        result = compute_frequency_60d(df, COL_MAP)
        assert result["A"] == 3


class TestComputeFrequency90d:
    def test_count_in_90d(self):
        df = _make_df([
            ("A", "2024-06-30", 10),
            ("A", "2024-06-01", 20),
            ("A", "2024-05-01", 30),
            ("A", "2024-04-05", 40),
            ("A", "2024-01-01", 50),  # outside 90d
        ])
        result = compute_frequency_90d(df, COL_MAP)
        assert result["A"] == 4


class TestComputeMonetaryTotal:
    def test_sum_equals_500(self):
        df = _make_df([
            ("A", "2024-06-01", 100),
            ("A", "2024-06-02", 200),
            ("A", "2024-06-03", 200),
        ])
        result = compute_monetary_total(df, COL_MAP)
        assert result["A"] == 500


class TestComputeMonetaryAvg:
    def test_mean_of_three(self):
        df = _make_df([
            ("A", "2024-06-01", 100),
            ("A", "2024-06-02", 200),
            ("A", "2024-06-03", 300),
        ])
        result = compute_monetary_avg(df, COL_MAP)
        assert result["A"] == 200.0


class TestComputeFrequencyTrend:
    def test_increasing_frequency(self):
        # 1 txn in first half, 3 in second half -> positive
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-10-01", 20),
            ("A", "2024-11-01", 30),
            ("A", "2024-12-01", 40),
        ])
        result = compute_frequency_trend(df, COL_MAP)
        assert result["A"] > 0

    def test_decreasing_frequency(self):
        # 3 txns in first half, 1 in second half -> negative
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-02-01", 20),
            ("A", "2024-03-01", 30),
            ("A", "2024-12-01", 40),
        ])
        result = compute_frequency_trend(df, COL_MAP)
        assert result["A"] < 0


class TestComputeMonetaryTrend:
    def test_higher_avg_in_second_half(self):
        df = _make_df([
            ("A", "2024-01-01", 100),
            ("A", "2024-02-01", 100),
            ("A", "2024-11-01", 500),
            ("A", "2024-12-01", 500),
        ])
        result = compute_monetary_trend(df, COL_MAP)
        assert result["A"] > 0


class TestComputeDaysBetweenPurchasesAvg:
    def test_known_gaps(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-11", 20),  # gap 10
            ("A", "2024-01-31", 30),  # gap 20
            ("A", "2024-03-01", 40),  # gap 30
        ])
        result = compute_days_between_purchases_avg(df, COL_MAP)
        assert result["A"] == 20.0

    def test_single_txn_returns_nan(self):
        df = _make_df([("A", "2024-01-01", 10)])
        result = compute_days_between_purchases_avg(df, COL_MAP)
        assert np.isnan(result["A"])


class TestComputeDaysBetweenPurchasesStd:
    def test_known_std(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-11", 20),  # gap 10
            ("A", "2024-01-31", 30),  # gap 20
            ("A", "2024-03-01", 40),  # gap 30
        ])
        result = compute_days_between_purchases_std(df, COL_MAP)
        expected_std = pd.Series([10.0, 20.0, 30.0]).std()
        assert abs(result["A"] - expected_std) < 0.01

    def test_fewer_than_3_txns_returns_nan(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-11", 20),
        ])
        result = compute_days_between_purchases_std(df, COL_MAP)
        assert np.isnan(result["A"])
