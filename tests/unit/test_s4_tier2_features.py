import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from app.stages.s4_features import (
    compute_basket_diversity,
    compute_category_concentration,
    compute_channel_diversity,
    compute_avg_basket_size,
    compute_peak_vs_offpeak_ratio,
    compute_order_size_trend,
    compute_product_mix_change,
    compute_region_loyalty,
    compute_weekend_vs_weekday,
    compute_repeat_product_rate,
    compute_max_gap_between_purchases,
    compute_purchase_regularity_score,
    _build_col_map,
    _get_available_tier2,
)


FULL_COL_MAP = {
    "customer_id": "cid",
    "transaction_date": "date",
    "amount": "amt",
    "product": "prod",
    "quantity": "qty",
    "category": "cat",
    "channel": "chan",
    "region": "reg",
}


def _make_df(rows, columns):
    return pd.DataFrame(rows, columns=columns)


class TestBasketDiversity:
    def test_four_products(self):
        df = _make_df([
            ("A", "2024-01-01", "P1"),
            ("A", "2024-01-02", "P2"),
            ("A", "2024-01-03", "P3"),
            ("A", "2024-01-04", "P4"),
        ], ["cid", "date", "prod"])
        col_map = {"customer_id": "cid", "product": "prod"}
        result = compute_basket_diversity(df, col_map)
        assert result["A"] == 4


class TestCategoryConcentration:
    def test_80_percent_one_category(self):
        df = _make_df([
            ("A", "C1"), ("A", "C1"), ("A", "C1"), ("A", "C1"), ("A", "C2"),
        ], ["cid", "cat"])
        col_map = {"customer_id": "cid", "category": "cat"}
        result = compute_category_concentration(df, col_map)
        assert result["A"] == 0.8


class TestChannelDiversity:
    def test_three_channels(self):
        df = _make_df([
            ("A", "online"), ("A", "store"), ("A", "mobile"),
        ], ["cid", "chan"])
        col_map = {"customer_id": "cid", "channel": "chan"}
        result = compute_channel_diversity(df, col_map)
        assert result["A"] == 3


class TestAvgBasketSize:
    def test_known_mean(self):
        df = _make_df([
            ("A", 2), ("A", 4), ("A", 6),
        ], ["cid", "qty"])
        col_map = {"customer_id": "cid", "quantity": "qty"}
        result = compute_avg_basket_size(df, col_map)
        assert result["A"] == 4.0


class TestPeakVsOffpeakRatio:
    def test_known_distribution(self):
        # 2 peak (Nov, Dec), 2 off-peak (Mar, Jun) -> ratio = 2/2 = 1.0
        df = _make_df([
            ("A", "2024-03-01", 10),
            ("A", "2024-06-01", 20),
            ("A", "2024-11-01", 30),
            ("A", "2024-12-01", 40),
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_peak_vs_offpeak_ratio(df, col_map)
        assert result["A"] == 1.0


class TestOrderSizeTrend:
    def test_increasing_trend(self):
        df = _make_df([
            ("A", "2024-01-01", 100),
            ("A", "2024-02-01", 100),
            ("A", "2024-11-01", 500),
            ("A", "2024-12-01", 500),
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date", "amount": "amt"}
        result = compute_order_size_trend(df, col_map)
        assert result["A"] > 0


class TestProductMixChange:
    def test_same_products_zero(self):
        df = _make_df([
            ("A", "2024-01-01", "P1"),
            ("A", "2024-02-01", "P2"),
            ("A", "2024-11-01", "P1"),
            ("A", "2024-12-01", "P2"),
        ], ["cid", "date", "prod"])
        col_map = {"customer_id": "cid", "transaction_date": "date", "product": "prod"}
        result = compute_product_mix_change(df, col_map)
        assert result["A"] == 0.0

    def test_different_products_one(self):
        df = _make_df([
            ("A", "2024-01-01", "P1"),
            ("A", "2024-02-01", "P2"),
            ("A", "2024-11-01", "P3"),
            ("A", "2024-12-01", "P4"),
        ], ["cid", "date", "prod"])
        col_map = {"customer_id": "cid", "transaction_date": "date", "product": "prod"}
        result = compute_product_mix_change(df, col_map)
        assert result["A"] == 1.0


class TestRegionLoyalty:
    def test_single_region(self):
        df = _make_df([
            ("A", "North"), ("A", "North"), ("A", "North"),
        ], ["cid", "reg"])
        col_map = {"customer_id": "cid", "region": "reg"}
        result = compute_region_loyalty(df, col_map)
        assert result["A"] == 1.0


class TestWeekendVsWeekday:
    def test_known_distribution(self):
        # 2024-01-06 is Saturday, 2024-01-07 is Sunday
        # 2024-01-08 is Monday, 2024-01-09 is Tuesday
        df = _make_df([
            ("A", "2024-01-06", 10),  # weekend
            ("A", "2024-01-07", 20),  # weekend
            ("A", "2024-01-08", 30),  # weekday
            ("A", "2024-01-09", 40),  # weekday
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_weekend_vs_weekday(df, col_map)
        # 2 weekend / 2 weekday = 1.0
        assert result["A"] == 1.0


class TestRepeatProductRate:
    def test_half_repeated(self):
        df = _make_df([
            ("A", "P1"), ("A", "P1"),  # P1 repeated
            ("A", "P2"), ("A", "P2"),  # P2 repeated
            ("A", "P3"),               # P3 not repeated
            ("A", "P4"),               # P4 not repeated
        ], ["cid", "prod"])
        col_map = {"customer_id": "cid", "product": "prod"}
        result = compute_repeat_product_rate(df, col_map)
        assert result["A"] == 0.5


class TestMaxGapBetweenPurchases:
    def test_known_max_gap(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-11", 20),  # gap 10
            ("A", "2024-02-10", 30),  # gap 30
            ("A", "2024-02-20", 40),  # gap 10
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_max_gap_between_purchases(df, col_map)
        assert result["A"] == 30

    def test_single_txn_returns_nan(self):
        df = _make_df([("A", "2024-01-01", 10)], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_max_gap_between_purchases(df, col_map)
        assert np.isnan(result["A"])


class TestPurchaseRegularityScore:
    def test_equal_gaps_near_one(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-11", 20),  # gap 10
            ("A", "2024-01-21", 30),  # gap 10
            ("A", "2024-01-31", 40),  # gap 10
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_purchase_regularity_score(df, col_map)
        assert result["A"] >= 0.95

    def test_high_variance_near_zero(self):
        df = _make_df([
            ("A", "2024-01-01", 10),
            ("A", "2024-01-02", 20),   # gap 1
            ("A", "2024-06-01", 30),   # gap 151
            ("A", "2024-06-02", 40),   # gap 1
        ], ["cid", "date", "amt"])
        col_map = {"customer_id": "cid", "transaction_date": "date"}
        result = compute_purchase_regularity_score(df, col_map)
        assert result["A"] <= 0.3


class TestBuildColMap:
    def test_filters_out_other(self):
        mapping = {
            "columns": [
                {"name": "col_a", "llm_role": "customer_id"},
                {"name": "col_b", "llm_role": "other"},
                {"name": "col_c", "llm_role": "amount"},
            ]
        }
        result = _build_col_map(mapping)
        assert "customer_id" in result
        assert "amount" in result
        assert "other" not in result
        assert len(result) == 2


class TestGetAvailableTier2:
    def test_returns_features_with_matching_roles(self):
        col_map = {
            "customer_id": "cid",
            "transaction_date": "date",
            "amount": "amt",
            "product": "prod",
        }
        result = _get_available_tier2(col_map)
        assert "basket_diversity" in result
        assert "product_mix_change" in result
        assert "repeat_product_rate" in result
        # category required but not present
        assert "category_concentration" not in result

    def test_minimal_col_map(self):
        col_map = {
            "customer_id": "cid",
            "transaction_date": "date",
            "amount": "amt",
        }
        result = _get_available_tier2(col_map)
        # Only features requiring just transaction_date or amount
        assert "peak_vs_offpeak_ratio" in result
        assert "order_size_trend" in result
        assert "weekend_vs_weekday" in result
        assert "basket_diversity" not in result
