import pytest
from unittest.mock import AsyncMock, patch

from app.agent.evaluator import check_rules, evaluate, SUCCESS_CRITERIA
from app.agent.model_trainer import ModelResult
from app.models.schemas import LLMEvaluationOutput


def _make_model_result(
    name="xgboost",
    auc=0.85,
    f1=0.7,
    top_importance=0.3,
    n_features=5,
):
    importances = []
    for i in range(n_features):
        imp = top_importance if i == 0 else round((1 - top_importance) / (n_features - 1), 4)
        importances.append({"feature": f"feature_{i}", "importance": imp})
    return ModelResult(
        name=name,
        model=None,
        metrics={"auc": auc, "precision": 0.8, "recall": 0.7, "f1": f1},
        confusion_matrix={"TP": 40, "FP": 10, "TN": 40, "FN": 10},
        feature_importance=importances,
        training_time=1.0,
    )


class TestCheckRules:
    def test_passes_when_all_criteria_met(self):
        result = check_rules([_make_model_result()])
        assert result["passed"] is True
        assert result["issues"] == []

    def test_fails_on_low_auc(self):
        result = check_rules([_make_model_result(auc=0.55)])
        assert result["passed"] is False
        assert any("AUC" in i for i in result["issues"])

    def test_fails_on_low_f1(self):
        result = check_rules([_make_model_result(f1=0.3)])
        assert result["passed"] is False
        assert any("F1" in i for i in result["issues"])

    def test_fails_on_feature_dominance(self):
        result = check_rules([_make_model_result(top_importance=0.85)])
        assert result["passed"] is False
        assert any("importance" in i.lower() for i in result["issues"])

    def test_fails_on_low_feature_diversity(self):
        # Only 2 features, both above 5%
        mr = _make_model_result(n_features=2, top_importance=0.6)
        result = check_rules([mr])
        assert result["passed"] is False
        assert any("features above 5%" in i for i in result["issues"])

    def test_no_models_fails(self):
        result = check_rules([])
        assert result["passed"] is False

    def test_custom_criteria(self):
        custom = {**SUCCESS_CRITERIA, "min_auc": 0.5}
        result = check_rules([_make_model_result(auc=0.55)], criteria=custom)
        assert result["passed"] is True


class TestEvaluate:
    @pytest.mark.asyncio
    async def test_fallback_on_llm_failure(self):
        with patch("app.agent.evaluator.generate_structured", side_effect=Exception("LLM down")):
            result = await evaluate([_make_model_result()])
            assert isinstance(result, LLMEvaluationOutput)
            assert result.quality_acceptable is True
            assert result.best_model == "xgboost"

    @pytest.mark.asyncio
    async def test_fallback_detects_issues(self):
        with patch("app.agent.evaluator.generate_structured", side_effect=Exception("LLM down")):
            result = await evaluate([_make_model_result(auc=0.5)])
            assert result.quality_acceptable is False

    @pytest.mark.asyncio
    async def test_calls_llm_with_structured_output(self):
        mock_output = LLMEvaluationOutput(
            leakage_detected=False,
            suspect_features=[],
            leakage_reasoning="No leakage found",
            quality_acceptable=True,
            best_model="xgboost",
            suggested_adjustments=[],
            reasoning="Model looks good",
        )
        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=mock_output):
            result = await evaluate([_make_model_result()])
            assert result.quality_acceptable is True
            assert result.leakage_detected is False

    @pytest.mark.asyncio
    async def test_leakage_detected_by_llm(self):
        mock_output = LLMEvaluationOutput(
            leakage_detected=True,
            suspect_features=["recency"],
            leakage_reasoning="Recency overlaps with churn definition",
            quality_acceptable=False,
            best_model="xgboost",
            suggested_adjustments=["Remove recency feature"],
            reasoning="Leakage via recency",
        )
        with patch("app.agent.evaluator.generate_structured", new_callable=AsyncMock, return_value=mock_output):
            result = await evaluate([_make_model_result()])
            assert result.leakage_detected is True
            assert "recency" in result.suspect_features
