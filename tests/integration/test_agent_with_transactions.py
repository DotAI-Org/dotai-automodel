"""
Test agent loop against the real transactions.csv file.

Uses mocked LLM calls for column mapping/hypothesis/evaluation/feature suggestion.
Tests the full data flow: CSV → features → multi-model training → evaluation → iteration.
"""

import os
import pytest
import pandas as pd
import json
from unittest.mock import AsyncMock, patch

from app.agent.loop import (
    run_agent,
    AgentState,
    set_agent_state,
    get_agent_state,
)
from app.models.schemas import (
    LLMEvaluationOutput,
    LLMFeatureSuggestionOutput,
    LLMFeatureSelectionOutput,
    DSLFeature,
)


CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_data",
    "transactions.csv",
)


def _build_session_from_csv(path: str) -> dict:
    """Load CSV and build a session dict mimicking completed stages 1-3."""
    df = pd.read_csv(path)
    # transactions.csv columns: user_id, transaction_date, quantity, price, revenue, segment
    column_mapping = {
        "columns": [
            {"name": "user_id", "llm_role": "customer_id", "dtype": "object", "confidence": 1.0},
            {"name": "transaction_date", "llm_role": "transaction_date", "dtype": "datetime64", "confidence": 1.0},
            {"name": "revenue", "llm_role": "amount", "dtype": "float64", "confidence": 0.95},
            {"name": "quantity", "llm_role": "quantity", "dtype": "int64", "confidence": 0.9},
            {"name": "price", "llm_role": "other", "dtype": "float64", "confidence": 0.5},
            {"name": "segment", "llm_role": "category", "dtype": "object", "confidence": 0.8},
        ]
    }

    col_map = {
        "customer_id": "user_id",
        "transaction_date": "transaction_date",
        "amount": "revenue",
        "quantity": "quantity",
        "category": "segment",
    }

    hypothesis = {
        "hypothesis": {
            "type": "e-commerce",
            "confidence": 0.9,
            "reasoning": "Transaction data with revenue, quantity, and customer segments",
        }
    }

    return {
        "created_at": 1000000,
        "stage": 3,
        "dataframe": df,
        "column_mapping": column_mapping,
        "hypothesis": hypothesis,
        "col_map": col_map,
        "mcq_answers": {},
        "profile": {
            "row_count": len(df),
            "columns": [{"name": c} for c in df.columns],
        },
    }


def _mock_eval_success():
    return LLMEvaluationOutput(
        leakage_detected=False,
        suspect_features=[],
        leakage_reasoning="No leakage detected",
        quality_acceptable=True,
        best_model="xgboost",
        suggested_adjustments=[],
        reasoning="Model metrics meet all criteria",
    )


def _mock_eval_leakage_iter1():
    return LLMEvaluationOutput(
        leakage_detected=True,
        suspect_features=["recency"],
        leakage_reasoning="Recency feature overlaps with churn window definition",
        quality_acceptable=False,
        best_model="xgboost",
        suggested_adjustments=["Remove recency", "Add DSL features for trend analysis"],
        reasoning="Single feature dominance detected",
    )


def _mock_feature_suggestion():
    return LLMFeatureSuggestionOutput(
        suggested_features=[
            DSLFeature(
                name="high_value_txn_count",
                description="Count of transactions with revenue > 50",
                operation="conditional_count",
                params_json=json.dumps({"column": "amount", "condition": "> 50"}),
            ),
            DSLFeature(
                name="product_diversity",
                description="Number of distinct segments purchased",
                operation="nunique",
                params_json=json.dumps({"column": "category"}),
            ),
        ],
        reasoning="Revenue threshold and segment diversity may indicate retention",
    )


@pytest.fixture
def session():
    if not os.path.exists(CSV_PATH):
        pytest.skip(f"Test CSV not found: {CSV_PATH}")
    return _build_session_from_csv(CSV_PATH)


class TestAgentWithTransactionsCSV:
    @pytest.mark.asyncio
    async def test_iteration1_trains_both_models(self, session):
        """Iteration 1 trains both XGBoost and RF on transactions.csv."""
        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=_mock_eval_success()), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=["category_concentration"]):

            state = AgentState(session_id="txn_test1")
            set_agent_state("txn_test1", state)
            result = await run_agent("txn_test1", session)

            assert result.status == "success"
            assert result.iteration == 1
            assert len(result.history) == 1

            # Both models trained
            model_names = {mr.name for mr in result.history[0].model_results}
            assert "xgboost" in model_names
            assert "random_forest" in model_names

            # All metrics present
            for mr in result.history[0].model_results:
                assert "auc" in mr.metrics
                assert "f1" in mr.metrics
                assert "precision" in mr.metrics
                assert "recall" in mr.metrics
                assert mr.metrics["auc"] > 0

            # Champion selected
            assert result.champion is not None
            assert result.champion.name in ("xgboost", "random_forest")
            print(f"\nChampion: {result.champion.name}")
            print(f"  AUC: {result.champion.metrics['auc']}")
            print(f"  F1: {result.champion.metrics['f1']}")
            print(f"  Features: {len(result.champion.feature_importance)}")

    @pytest.mark.asyncio
    async def test_leakage_removal_and_dsl_feature_addition(self, session):
        """Leakage detected on iter 1 → removes recency → adds DSL features → succeeds on iter 2."""
        eval_count = 0

        async def mock_eval(*args, **kwargs):
            nonlocal eval_count
            eval_count += 1
            if eval_count == 1:
                return _mock_eval_leakage_iter1()
            return _mock_eval_success()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, side_effect=mock_eval), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]), \
             patch("app.agent.feature_engineer.generate_structured", new_callable=AsyncMock, return_value=_mock_feature_suggestion()):

            state = AgentState(session_id="txn_test2")
            set_agent_state("txn_test2", state)
            result = await run_agent("txn_test2", session)

            assert result.iteration == 2
            assert "recency" in result.excluded_features

            # DSL features were added
            dsl_names = [f.name for f in result.dsl_features]
            assert "high_value_txn_count" in dsl_names
            assert "product_diversity" in dsl_names

            # Iteration 2 features do not include recency
            iter2_features = result.history[1].features_used
            assert "recency" not in iter2_features

            # DSL features are in iteration 2
            assert "high_value_txn_count" in iter2_features or "product_diversity" in iter2_features

            # Champion selected
            assert result.champion is not None
            print(f"\nIteration 1 features: {result.history[0].features_used}")
            print(f"Iteration 2 features: {result.history[1].features_used}")
            print(f"Champion: {result.champion.name} AUC={result.champion.metrics['auc']}")

    @pytest.mark.asyncio
    async def test_comparison_table_across_iterations(self, session):
        """All iterations produce comparable metrics for both models."""
        eval_count = 0

        async def mock_eval(*args, **kwargs):
            nonlocal eval_count
            eval_count += 1
            if eval_count <= 2:
                return LLMEvaluationOutput(
                    leakage_detected=False,
                    suspect_features=[],
                    leakage_reasoning="",
                    quality_acceptable=False,
                    best_model="xgboost",
                    suggested_adjustments=["Try more features"],
                    reasoning="Metrics below threshold",
                )
            return _mock_eval_success()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, side_effect=mock_eval), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]), \
             patch("app.agent.feature_engineer.generate_structured", new_callable=AsyncMock, return_value=_mock_feature_suggestion()):

            state = AgentState(session_id="txn_test3", max_iterations=3)
            set_agent_state("txn_test3", state)
            result = await run_agent("txn_test3", session)

            assert result.iteration == 3
            assert len(result.history) == 3

            # Build comparison table
            print("\n--- Comparison Table ---")
            print(f"{'Iter':<6}{'Model':<16}{'AUC':<8}{'F1':<8}{'Prec':<8}{'Recall':<8}")
            for h in result.history:
                for mr in h.model_results:
                    print(f"{h.iteration:<6}{mr.name:<16}{mr.metrics['auc']:<8}{mr.metrics['f1']:<8}{mr.metrics['precision']:<8}{mr.metrics['recall']:<8}")

            # Verify serialization works
            state_dict = result.to_dict()
            assert len(state_dict["history"]) == 3
            assert state_dict["champion"] is not None
