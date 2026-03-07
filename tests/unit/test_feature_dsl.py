import pytest
import pandas as pd
import numpy as np
import json

from app.models.schemas import DSLFeature
from app.agent.feature_dsl import execute_dsl_feature, execute_dsl_features


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "cust": ["A", "A", "A", "B", "B", "C"],
        "date": pd.to_datetime([
            "2024-01-01", "2024-02-01", "2024-03-01",
            "2024-01-15", "2024-03-15",
            "2024-02-15",
        ]),
        "amt": [100, 200, 150, 50, 75, 300],
        "product": ["X", "Y", "X", "X", "Z", "Y"],
        "qty": [1, 2, 3, 1, 2, 5],
    })


@pytest.fixture
def col_map():
    return {
        "customer_id": "cust",
        "transaction_date": "date",
        "amount": "amt",
        "product": "product",
        "quantity": "qty",
    }


class TestAggregate:
    def test_sum(self, sample_df, col_map):
        feat = DSLFeature(
            name="total_spend",
            description="Total spend per customer",
            operation="aggregate",
            params_json=json.dumps({"column": "amount", "func": "sum"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        assert result["A"] == 450
        assert result["B"] == 125
        assert result["C"] == 300

    def test_mean(self, sample_df, col_map):
        feat = DSLFeature(
            name="avg_spend",
            description="Average spend",
            operation="aggregate",
            params_json=json.dumps({"column": "amount", "func": "mean"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        assert result["A"] == 150
        assert result["B"] == 62.5


class TestAggregateWindow:
    def test_sum_30d(self, sample_df, col_map):
        feat = DSLFeature(
            name="recent_spend",
            description="Spend in last 30 days",
            operation="aggregate_window",
            params_json=json.dumps({"column": "amount", "func": "sum", "window_days": 30}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # Max date is 2024-03-15, cutoff is 2024-02-14
        # A: 150 (2024-03-01), B: 75 (2024-03-15), C: 300 (2024-02-15)
        assert result["A"] == 150
        assert result["B"] == 75
        assert result["C"] == 300

    def test_empty_window_returns_zero(self, sample_df, col_map):
        feat = DSLFeature(
            name="recent_spend",
            description="Spend in last 1 day",
            operation="aggregate_window",
            params_json=json.dumps({"column": "amount", "func": "sum", "window_days": 1}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # Only B has data on max date (2024-03-15)
        assert result["A"] == 0
        assert result["B"] == 75


class TestRatio:
    def test_recent_spend_ratio(self, sample_df, col_map):
        feat = DSLFeature(
            name="recent_ratio",
            description="Recent vs total spend ratio",
            operation="ratio",
            params_json=json.dumps({
                "numerator": {"column": "amount", "func": "sum", "window_days": 30},
                "denominator": {"column": "amount", "func": "sum"},
            }),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        assert abs(result["A"] - 150 / 450) < 0.01
        assert abs(result["B"] - 75 / 125) < 0.01


class TestTrend:
    def test_amount_trend(self, sample_df, col_map):
        feat = DSLFeature(
            name="amt_trend",
            description="Amount trend",
            operation="trend",
            params_json=json.dumps({"column": "amount", "func": "mean"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # Mid date = 2024-01-01 + (2024-03-15 - 2024-01-01)/2 ≈ 2024-02-07
        # A first half: [100, 200] mean=150, second half: [150] mean=150 -> trend=0
        # (Feb 1 is before Feb 7 mid, Mar 1 is after)
        # Check that A has a numeric result
        assert isinstance(result["A"], (int, float, np.integer, np.floating))


class TestConditionalCount:
    def test_high_value_count(self, sample_df, col_map):
        feat = DSLFeature(
            name="high_value_txns",
            description="Transactions > 100",
            operation="conditional_count",
            params_json=json.dumps({"column": "amount", "condition": "> 100"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # A: 200, 150 -> 2; B: none -> 0; C: 300 -> 1
        assert result["A"] == 2
        assert result["B"] == 0
        assert result["C"] == 1

    def test_equality_condition(self, sample_df, col_map):
        feat = DSLFeature(
            name="product_x_count",
            description="Product X transactions",
            operation="conditional_count",
            params_json=json.dumps({"column": "product", "condition": "== 'X'"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        assert result["A"] == 2
        assert result["B"] == 1
        assert result["C"] == 0


class TestNunique:
    def test_product_diversity(self, sample_df, col_map):
        feat = DSLFeature(
            name="product_count",
            description="Distinct products",
            operation="nunique",
            params_json=json.dumps({"column": "product"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        assert result["A"] == 2  # X, Y
        assert result["B"] == 2  # X, Z
        assert result["C"] == 1  # Y


class TestGapStat:
    def test_max_gap(self, sample_df, col_map):
        feat = DSLFeature(
            name="max_gap",
            description="Max gap between purchases",
            operation="gap_stat",
            params_json=json.dumps({"func": "max"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # A: gaps are 31 (Jan 1->Feb 1), 29 (Feb 1->Mar 1) -> max=31
        assert result["A"] == 31
        # B: gap is 60 (Jan 15 -> Mar 15)
        assert result["B"] == 60
        # C: single purchase -> NaN
        assert np.isnan(result["C"])

    def test_mean_gap(self, sample_df, col_map):
        feat = DSLFeature(
            name="avg_gap",
            description="Avg gap between purchases",
            operation="gap_stat",
            params_json=json.dumps({"func": "mean"}),
        )
        result = execute_dsl_feature(sample_df, col_map, feat)
        # A: gaps 31, 29 -> mean=30
        assert abs(result["A"] - 30) < 1
        # B: gap 60 -> mean=60
        assert result["B"] == 60


class TestExecuteMultiple:
    def test_multiple_features(self, sample_df, col_map):
        features = [
            DSLFeature(name="total", description="", operation="aggregate",
                       params_json=json.dumps({"column": "amount", "func": "sum"})),
            DSLFeature(name="products", description="", operation="nunique",
                       params_json=json.dumps({"column": "product"})),
        ]
        result = execute_dsl_features(sample_df, col_map, features)
        assert "total" in result.columns
        assert "products" in result.columns
        assert len(result) == 3

    def test_excluded_features_skipped(self, sample_df, col_map):
        features = [
            DSLFeature(name="total", description="", operation="aggregate",
                       params_json=json.dumps({"column": "amount", "func": "sum"})),
            DSLFeature(name="products", description="", operation="nunique",
                       params_json=json.dumps({"column": "product"})),
        ]
        result = execute_dsl_features(sample_df, col_map, features, excluded=["total"])
        assert "total" not in result.columns
        assert "products" in result.columns

    def test_bad_feature_skipped(self, sample_df, col_map):
        features = [
            DSLFeature(name="bad", description="", operation="aggregate",
                       params_json=json.dumps({"column": "nonexistent", "func": "sum"})),
            DSLFeature(name="good", description="", operation="nunique",
                       params_json=json.dumps({"column": "product"})),
        ]
        result = execute_dsl_features(sample_df, col_map, features)
        assert "bad" not in result.columns
        assert "good" in result.columns


class TestUnknownOperation:
    def test_raises_on_unknown_op(self, sample_df, col_map):
        feat = DSLFeature(
            name="bad",
            description="",
            operation="nonexistent_op",
            params_json=json.dumps({}),
        )
        with pytest.raises(ValueError, match="Unknown DSL operation"):
            execute_dsl_feature(sample_df, col_map, feat)
