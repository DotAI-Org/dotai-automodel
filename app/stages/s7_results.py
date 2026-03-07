from typing import Any
from fastapi import HTTPException

from app.models.schemas import (
    ResultsResponse,
    FeatureImportance,
    SamplePrediction,
    RiskTier,
    LLMResultsSummaryOutput,
)
from app.llm.client import generate_structured


async def handle(session_id: str, session: dict[str, Any]) -> ResultsResponse:
    metrics = session.get("metrics")
    model = session.get("model")
    X_test = session.get("X_test")
    y_test = session.get("y_test")
    feature_importance = session.get("feature_importance")

    if metrics is None or model is None or X_test is None:
        raise HTTPException(
            status_code=400,
            detail="Model training must be completed first.",
        )

    # Generate sample predictions from test set
    y_proba = model.predict_proba(X_test)[:, 1]
    sample_predictions = []
    for i, (idx, prob) in enumerate(zip(X_test.index, y_proba)):
        if i >= 20:
            break
        tier = _get_risk_tier(prob)
        actual = bool(y_test.loc[idx]) if idx in y_test.index else None
        sample_predictions.append(SamplePrediction(
            customer_id=str(idx),
            churn_probability=round(float(prob), 4),
            risk_tier=tier,
            actual_churned=actual,
        ))

    # LLM summary
    hypothesis = session.get("hypothesis", {})
    business_type = hypothesis.get("hypothesis", {}).get("type", "Unknown")

    summary = await _generate_summary(metrics, feature_importance, business_type)

    feat_imp_objs = [FeatureImportance(**fi) for fi in feature_importance]

    return ResultsResponse(
        summary=summary,
        metrics=metrics,
        feature_importance=feat_imp_objs,
        sample_predictions=sample_predictions,
    )


def _get_risk_tier(probability: float) -> RiskTier:
    if probability > 0.7:
        return RiskTier.high
    elif probability > 0.4:
        return RiskTier.medium
    return RiskTier.low


async def _generate_summary(
    metrics: dict, feature_importance: list[dict], business_type: str
) -> str:
    feat_text = "\n".join(
        f"- {fi['feature']}: {fi['importance']}" for fi in feature_importance[:5]
    )

    prompt = f"""You are a data scientist writing a results summary for a churn prediction model.

Business type: {business_type}

Model metrics:
- AUC-ROC: {metrics['auc']}
- Precision: {metrics['precision']}
- Recall: {metrics['recall']}
- F1 Score: {metrics['f1']}

Top features by importance:
{feat_text}

Write a 3-5 sentence summary in plain business language. Explain:
1. How well the model performs (interpret the metrics)
2. What the top predictors of churn are (translate feature names to business concepts)
3. One actionable insight

Return JSON with a "summary" field containing the text."""

    result = await generate_structured(prompt, LLMResultsSummaryOutput)
    return result.summary
