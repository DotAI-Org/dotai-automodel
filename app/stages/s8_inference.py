"""Stage 8: Churn inference with SHAP-based feature contributions."""
import io
import logging
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException
import shap

from app.session_store import store
from app.models.schemas import (
    InferenceResponse,
    InferencePrediction,
    FeatureContribution,
    RiskTier,
)

logger = logging.getLogger(__name__)


def handle(session_id: str, session: dict[str, Any]) -> InferenceResponse:
    """Run churn predictions on all customers with SHAP explanations."""
    model = session.get("model")
    feature_matrix = session.get("feature_matrix")
    feature_names = session.get("feature_names")

    if model is None or feature_matrix is None:
        raise HTTPException(
            status_code=400,
            detail="Model training must be completed first.",
        )

    tier_map = session.get("feature_tier_map", {})
    detected_types = session.get("detected_data_types", [1])
    has_multi_source = session.get("field_analysis_signature") is not None

    # Use model's own feature names as ground truth when available
    model_features = getattr(model, "feature_names_in_", None)
    if model_features is not None:
        feature_names = list(model_features)
    else:
        feature_names = list(feature_names)

    # Align columns to what the model was trained on
    for col in feature_names:
        if col not in feature_matrix.columns:
            feature_matrix[col] = 0
    X = feature_matrix[feature_names].copy()
    X = X.fillna(0)

    # Predict probabilities
    probabilities = model.predict_proba(X)[:, 1]

    # Compute SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    predictions = []
    high_count = 0
    medium_count = 0
    low_count = 0

    for i, (idx, prob) in enumerate(zip(X.index, probabilities)):
        tier = _get_risk_tier(prob)
        if tier == RiskTier.high:
            high_count += 1
        elif tier == RiskTier.medium:
            medium_count += 1
        else:
            low_count += 1

        # Top 3 SHAP contributions
        shap_row = shap_values[i]
        if shap_row.ndim > 1:
            shap_row = shap_row.flatten()
        n_feats = min(len(shap_row), len(feature_names))
        shap_row_trimmed = shap_row[:n_feats]
        top_indices = np.argsort(np.abs(shap_row_trimmed))[-3:][::-1]

        top_features = []
        for j in top_indices:
            feat_name = feature_names[int(j)]
            feat_tier = tier_map.get(feat_name)
            feat_source = _tier_to_source(feat_tier) if feat_tier else None
            top_features.append(FeatureContribution(
                feature=feat_name,
                contribution=round(float(shap_row_trimmed[int(j)]), 4),
                tier=feat_tier,
                source=feat_source,
            ))

        # Action recommendation for multi-source
        action = None
        if has_multi_source:
            action = _generate_action(top_features, detected_types)

        predictions.append(InferencePrediction(
            customer_id=str(idx),
            churn_probability=round(float(prob), 4),
            risk_tier=tier,
            top_features=top_features,
            action=action,
        ))

    # Sort by probability descending
    predictions.sort(key=lambda p: p.churn_probability, reverse=True)

    # Check if agent loop is still running — if so, update in-memory only
    # to avoid blocking the event loop with heavy blob serialization
    from app.agent.loop import get_agent_state
    agent_state = get_agent_state(session_id)
    if agent_state and agent_state.status == "running":
        session = store.get(session_id)
        if session:
            session.update({"stage": 8, "predictions": predictions})
    else:
        store.update(session_id, {
            "stage": 8,
            "predictions": predictions,
        })

    return InferenceResponse(
        total_users=len(predictions),
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        predictions=predictions,
    )


def handle_download(session_id: str, session: dict[str, Any]) -> io.StringIO:
    """Generate a CSV download buffer from stored predictions."""
    predictions = session.get("predictions")
    if not predictions:
        raise HTTPException(
            status_code=400,
            detail="Inference must be completed first.",
        )

    tier_map = session.get("feature_tier_map", {})
    has_multi_source = session.get("field_analysis_signature") is not None

    rows = []
    for pred in predictions:
        if isinstance(pred, dict):
            customer_id = pred.get("customer_id", "")
            churn_prob = pred.get("churn_probability", 0)
            risk_tier = pred.get("risk_tier", "")
            if hasattr(risk_tier, "value"):
                risk_tier = risk_tier.value
            top_features = pred.get("top_features", [])
            action = pred.get("action", "")
        else:
            customer_id = pred.customer_id
            churn_prob = pred.churn_probability
            risk_tier = pred.risk_tier.value
            top_features = pred.top_features
            action = pred.action or ""

        row = {
            "customer_id": customer_id,
            "churn_probability": churn_prob,
            "risk_tier": risk_tier,
        }

        # Add top features with source info
        for idx, fc in enumerate(top_features[:3]):
            if isinstance(fc, dict):
                feat = fc.get("feature", "")
                contrib = fc.get("contribution", 0)
                source = fc.get("source", "")
            else:
                feat = fc.feature
                contrib = fc.contribution
                source = fc.source or ""

            row[f"top_feature_{idx + 1}"] = feat
            row[f"top_feature_{idx + 1}_contribution"] = contrib
            if has_multi_source:
                row[f"top_feature_{idx + 1}_source"] = source

        if has_multi_source:
            row["action"] = action

        rows.append(row)

    df = pd.DataFrame(rows)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def _get_risk_tier(probability: float) -> RiskTier:
    """Map a churn probability to a risk tier."""
    if probability > 0.7:
        return RiskTier.high
    elif probability > 0.4:
        return RiskTier.medium
    return RiskTier.low


def _tier_to_source(tier: int) -> str:
    """Map feature tier to data source label."""
    return {
        1: "transaction",
        2: "product/category",
        3: "secondary_data",
        4: "other_fields",
    }.get(tier, "unknown")


def _generate_action(
    top_features: list[FeatureContribution], detected_types: list
) -> str:
    """Generate action recommendation based on top contributing features."""
    actions = []
    for feat in top_features:
        feat_name = feat.feature
        feat_tier = feat.tier

        if feat_tier == 3:
            if 3 in detected_types:  # loyalty
                if "points" in feat_name or "earn" in feat_name:
                    actions.append(
                        "Check loyalty program engagement. Points activity has declined."
                    )
                elif "tier" in feat_name:
                    actions.append(
                        "Tier downgrade detected. Consider retention offer."
                    )
            if 2 in detected_types:  # service
                if "ticket" in feat_name or "csat" in feat_name:
                    actions.append(
                        "Open service complaints. Resolve before expecting orders."
                    )
                if "warranty" in feat_name:
                    actions.append(
                        "Warranty expiring. Trigger renewal outreach."
                    )
            if 5 in detected_types:  # field
                if "visit" in feat_name:
                    actions.append(
                        "Rep visit frequency has dropped. Schedule visit."
                    )
        elif feat_tier == 4:
            if "payment_terms" in feat_name:
                actions.append(
                    "Review payment terms. Credit pressure may be a factor."
                )

    return actions[0] if actions else "Review account and schedule contact."
