"""Stage 7: Model results summary with LLM-generated text."""
import logging
from typing import Any

import numpy as np
from fastapi import HTTPException
import shap

from app.session_store import store
from app.models.schemas import (
    ResultsResponse,
    FeatureImportance,
    SamplePrediction,
    RiskTier,
    LLMResultsSummaryOutput,
)
from app.llm.client import generate_structured

logger = logging.getLogger(__name__)


async def handle(session_id: str, session: dict[str, Any]) -> ResultsResponse:
    """Build results response with sample predictions and LLM summary."""
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

    # Check for multi-model results
    model_comparison = session.get("model_comparison")
    lift = session.get("lift")
    tier_attribution = session.get("tier_attribution")
    tier_map = session.get("feature_tier_map", {})

    has_multi_model = model_comparison is not None

    if has_multi_model:
        # Multi-model path: enriched summary with lift and attribution
        sample_predictions = _build_sample_predictions(
            model, X_test, y_test, tier_map
        )

        summary = await _generate_enriched_summary(
            metrics=metrics,
            feature_importance=feature_importance,
            lift=lift,
            tier_attribution=tier_attribution,
            leakage_report=session.get("leakage_report", {}),
            detected_types=session.get("detected_data_types", [1]),
            findings=session.get("findings", {}),
            hypothesis=session.get("hypothesis", {}),
        )

        # Build comparison dict with metrics only (no model objects)
        comparison_metrics = {}
        for k, v in model_comparison.items():
            comparison_metrics[k] = {
                "name": v.get("name", k),
                "metrics": v.get("metrics", {}),
            }

        feat_imp_objs = [FeatureImportance(**fi) for fi in feature_importance]

        store.update(session_id, {
            "stage": 7,
            "summary": summary,
        })

        return ResultsResponse(
            summary=summary,
            metrics=metrics,
            feature_importance=feat_imp_objs,
            sample_predictions=sample_predictions,
            model_comparison=comparison_metrics,
            lift=lift,
            tier_attribution=tier_attribution,
        )

    # Legacy single-model path
    sample_predictions = _build_legacy_predictions(model, X_test, y_test)

    hypothesis = session.get("hypothesis", {})
    business_type = hypothesis.get("hypothesis", {}).get("type", "Unknown")
    summary = await _generate_summary(metrics, feature_importance, business_type)

    feat_imp_objs = [FeatureImportance(**fi) for fi in feature_importance]

    store.update(session_id, {
        "stage": 7,
        "summary": summary,
    })

    return ResultsResponse(
        summary=summary,
        metrics=metrics,
        feature_importance=feat_imp_objs,
        sample_predictions=sample_predictions,
    )


def _build_legacy_predictions(model, X_test, y_test) -> list[SamplePrediction]:
    """Build sample predictions for legacy single-model path."""
    y_proba = model.predict_proba(X_test)[:, 1]
    predictions = []
    for i, (idx, prob) in enumerate(zip(X_test.index, y_proba)):
        if i >= 20:
            break
        tier = _get_risk_tier(prob)
        actual = bool(y_test.loc[idx]) if idx in y_test.index else None
        predictions.append(SamplePrediction(
            customer_id=str(idx),
            churn_probability=round(float(prob), 4),
            risk_tier=tier,
            actual_churned=actual,
        ))
    return predictions


def _build_sample_predictions(
    model, X_test, y_test, tier_map: dict
) -> list[SamplePrediction]:
    """Build sample predictions with SHAP-based multi-source context."""
    y_proba = model.predict_proba(X_test)[:, 1]

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        has_shap = True
    except Exception:
        has_shap = False

    predictions = []
    for i, (idx, prob) in enumerate(zip(X_test.index, y_proba)):
        if i >= 20:
            break
        tier = _get_risk_tier(prob)
        actual = bool(y_test.loc[idx]) if idx in y_test.index else None
        predictions.append(SamplePrediction(
            customer_id=str(idx),
            churn_probability=round(float(prob), 4),
            risk_tier=tier,
            actual_churned=actual,
        ))
    return predictions


async def _generate_enriched_summary(
    metrics: dict,
    feature_importance: list[dict],
    lift: dict | None,
    tier_attribution: dict | None,
    leakage_report: dict,
    detected_types: list,
    findings: dict,
    hypothesis: dict,
) -> str:
    """Generate summary enriched with multi-source context."""
    business_type = hypothesis.get("hypothesis", {}).get("type", "Unknown")

    feat_text = "\n".join(
        f"- {fi['feature']}: {fi['importance']}" for fi in feature_importance[:5]
    )

    prompt = f"""You are a data scientist writing a results summary for a Sales VP.

Business type: {business_type}

Model metrics:
- AUC-ROC: {metrics.get('auc', 'N/A')}
- Precision: {metrics.get('precision', 'N/A')}
- Recall: {metrics.get('recall', 'N/A')}
- F1 Score: {metrics.get('f1', 'N/A')}

Top features by importance:
{feat_text}
"""

    if lift:
        prompt += f"""
Data enrichment impact:
- Baseline (transactions only): F1 = {lift.get('f1_baseline', 'N/A')}
- Enriched (all data sources): F1 = {lift.get('f1_enriched', 'N/A')}
- Lift: +{lift.get('f1_lift', 'N/A')}
"""

    if tier_attribution:
        prompt += f"""
Signal attribution by source:
{tier_attribution}
"""

    signals = findings.get("signals", [])
    if signals:
        signal_text = "\n".join(
            f"- {s.get('field', '')}: AUC={s.get('auc', '')}" for s in signals[:3]
        )
        prompt += f"""
Key signals from data analysis:
{signal_text}
"""

    if leakage_report:
        prompt += f"""
Leakage checks:
- Suspects found: {len(leakage_report.get('suspects', []))}
- Removed: {len(leakage_report.get('removed', []))}
- Kept as leading indicators: {len(leakage_report.get('kept_as_leading', []))}
"""

    prompt += """
Write a 3-5 sentence summary in plain language. No jargon. Focus on:
1. How well the model performs
2. What the top predictors of churn are (translate to business concepts)
3. Whether additional data sources improved predictions
4. One actionable insight

Return JSON with a "summary" field containing the text."""

    result = await generate_structured(prompt, LLMResultsSummaryOutput)
    return result.summary


def _get_risk_tier(probability: float) -> RiskTier:
    """Map a churn probability to a risk tier."""
    if probability > 0.7:
        return RiskTier.high
    elif probability > 0.4:
        return RiskTier.medium
    return RiskTier.low


async def _generate_summary(
    metrics: dict, feature_importance: list[dict], business_type: str
) -> str:
    """Generate a text summary of model results using LLM."""
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
