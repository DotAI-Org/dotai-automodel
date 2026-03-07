import pytest
import pandas as pd
import numpy as np
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


def _make_session():
    """Build a session dict with stages 1-3 completed."""
    np.random.seed(42)
    n_custs = 50
    rows = []
    for i in range(n_custs):
        cid = f"C{i:03d}"
        n_txns = np.random.randint(3, 20)
        for _ in range(n_txns):
            date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=np.random.randint(0, 300))
            rows.append({
                "customer_id": cid,
                "date": date,
                "amount": round(np.random.uniform(10, 500), 2),
                "product": np.random.choice(["A", "B", "C", "D"]),
                "quantity": np.random.randint(1, 10),
            })

    df = pd.DataFrame(rows)

    column_mapping = {
        "columns": [
            {"name": "customer_id", "llm_role": "customer_id", "dtype": "object", "confidence": 1.0},
            {"name": "date", "llm_role": "transaction_date", "dtype": "datetime64", "confidence": 1.0},
            {"name": "amount", "llm_role": "amount", "dtype": "float64", "confidence": 1.0},
            {"name": "product", "llm_role": "product", "dtype": "object", "confidence": 0.9},
            {"name": "quantity", "llm_role": "quantity", "dtype": "int64", "confidence": 0.9},
        ]
    }

    hypothesis = {
        "hypothesis": {
            "type": "e-commerce",
            "confidence": 0.85,
            "reasoning": "Transaction data with products and amounts",
        }
    }

    col_map = {
        "customer_id": "customer_id",
        "transaction_date": "date",
        "amount": "amount",
        "product": "product",
        "quantity": "quantity",
    }

    return {
        "created_at": 1000000,
        "stage": 3,
        "dataframe": df,
        "column_mapping": column_mapping,
        "hypothesis": hypothesis,
        "col_map": col_map,
        "mcq_answers": {},
        "profile": {},
    }


def _mock_evaluation_success():
    return LLMEvaluationOutput(
        leakage_detected=False,
        suspect_features=[],
        leakage_reasoning="No leakage",
        quality_acceptable=True,
        best_model="xgboost",
        suggested_adjustments=[],
        reasoning="Model meets criteria",
    )


def _mock_evaluation_leakage():
    return LLMEvaluationOutput(
        leakage_detected=True,
        suspect_features=["recency"],
        leakage_reasoning="Recency overlaps with churn definition",
        quality_acceptable=False,
        best_model="xgboost",
        suggested_adjustments=["Remove recency"],
        reasoning="Leakage via recency",
    )


def _mock_feature_selection():
    return LLMFeatureSelectionOutput(
        selected_features=["basket_diversity"],
        reasoning="Product diversity matters",
    )


def _mock_feature_suggestion():
    return LLMFeatureSuggestionOutput(
        suggested_features=[
            DSLFeature(
                name="high_value_txns",
                description="Count of transactions > 100",
                operation="conditional_count",
                params_json=json.dumps({"column": "amount", "condition": "> 100"}),
            )
        ],
        reasoning="High-value transaction count may predict retention",
    )


class TestAgentLoop:
    @pytest.mark.asyncio
    async def test_success_on_first_iteration(self):
        """Agent finds a model that meets criteria on iteration 1."""
        session = _make_session()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=_mock_evaluation_success()), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=["basket_diversity"]):

            state = AgentState(session_id="test1")
            set_agent_state("test1", state)
            result = await run_agent("test1", session)

            assert result.status == "success"
            assert result.iteration == 1
            assert result.champion is not None
            assert len(result.history) == 1

    @pytest.mark.asyncio
    async def test_leakage_triggers_second_iteration(self):
        """Agent detects leakage, removes feature, succeeds on iteration 2."""
        session = _make_session()

        eval_call_count = 0

        async def mock_evaluate(*args, **kwargs):
            nonlocal eval_call_count
            eval_call_count += 1
            if eval_call_count == 1:
                return _mock_evaluation_leakage()
            return _mock_evaluation_success()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, side_effect=mock_evaluate), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]), \
             patch("app.agent.feature_engineer.generate_structured", new_callable=AsyncMock, return_value=_mock_feature_suggestion()):

            state = AgentState(session_id="test2")
            set_agent_state("test2", state)
            result = await run_agent("test2", session)

            assert result.iteration == 2
            assert "recency" in result.excluded_features
            assert result.champion is not None
            assert len(result.history) == 2

    @pytest.mark.asyncio
    async def test_max_iterations_reached(self):
        """Agent reaches max iterations and picks best model."""
        session = _make_session()

        mock_eval_fail = LLMEvaluationOutput(
            leakage_detected=False,
            suspect_features=[],
            leakage_reasoning="",
            quality_acceptable=False,
            best_model="xgboost",
            suggested_adjustments=["Try more features"],
            reasoning="Metrics below threshold",
        )

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=mock_eval_fail), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]), \
             patch("app.agent.feature_engineer.generate_structured", new_callable=AsyncMock, return_value=_mock_feature_suggestion()):

            state = AgentState(session_id="test3", max_iterations=2)
            set_agent_state("test3", state)
            result = await run_agent("test3", session)

            assert result.status in ("completed", "running")
            assert result.iteration == 2
            assert result.champion is not None

    @pytest.mark.asyncio
    async def test_user_override_stops_agent(self):
        """User override with stop=True interrupts the loop."""
        session = _make_session()

        async def mock_evaluate(*args, **kwargs):
            # Inject stop override before returning
            s = get_agent_state("test4")
            if s and s.iteration >= 1:
                s.user_overrides["stop"] = True
            return _mock_evaluation_leakage()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, side_effect=mock_evaluate), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]):

            state = AgentState(session_id="test4", max_iterations=5)
            set_agent_state("test4", state)
            result = await run_agent("test4", session)

            assert result.status == "interrupted"
            assert result.iteration <= 2

    @pytest.mark.asyncio
    async def test_state_serialization(self):
        """Agent state can be serialized to dict for API responses."""
        session = _make_session()

        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=_mock_evaluation_success()), \
             patch("app.stages.s4_features._select_tier2_features", new_callable=AsyncMock, return_value=[]):

            state = AgentState(session_id="test5")
            set_agent_state("test5", state)
            result = await run_agent("test5", session)

            state_dict = result.to_dict()
            assert state_dict["session_id"] == "test5"
            assert state_dict["status"] == "success"
            assert state_dict["champion"] is not None
            assert isinstance(state_dict["history"], list)
