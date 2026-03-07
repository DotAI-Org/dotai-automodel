from typing import Any
import io
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


def handle(session_id: str, session: dict[str, Any]) -> InferenceResponse:
    model = session.get("model")
    feature_matrix = session.get("feature_matrix")
    feature_names = session.get("feature_names")

    if model is None or feature_matrix is None:
        raise HTTPException(
            status_code=400,
            detail="Model training must be completed first.",
        )

    # Use model's own feature names as ground truth when available
    model_features = getattr(model, "feature_names_in_", None)
    if model_features is not None:
        feature_names = list(model_features)
    else:
        feature_names = list(feature_names)

    # Prepare feature matrix (align columns to what the model was trained on)
    # Add missing columns as 0, drop extra columns not seen during fit
    for col in feature_names:
        if col not in feature_matrix.columns:
            feature_matrix[col] = 0
    X = feature_matrix[feature_names].copy()
    X = X.fillna(0)

    # Predict probabilities
    probabilities = model.predict_proba(X)[:, 1]

    # Compute SHAP values for top feature contributions
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    # For binary classifiers, shap_values is a list of 2 arrays; use positive class
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
        # Clamp to feature_names length in case of dimension mismatch
        n_feats = min(len(shap_row), len(feature_names))
        shap_row_trimmed = shap_row[:n_feats]
        top_indices = np.argsort(np.abs(shap_row_trimmed))[-3:][::-1]
        top_features = [
            FeatureContribution(
                feature=feature_names[int(j)],
                contribution=round(float(shap_row_trimmed[int(j)]), 4),
            )
            for j in top_indices
        ]

        predictions.append(InferencePrediction(
            customer_id=str(idx),
            churn_probability=round(float(prob), 4),
            risk_tier=tier,
            top_features=top_features,
        ))

    # Store predictions for download
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
    predictions = session.get("predictions")
    if not predictions:
        raise HTTPException(
            status_code=400,
            detail="Inference must be completed first.",
        )

    rows = []
    for pred in predictions:
        # Handle both Pydantic objects and plain dicts (after pickle reload)
        if isinstance(pred, dict):
            customer_id = pred.get("customer_id", "")
            churn_prob = pred.get("churn_probability", 0)
            risk_tier = pred.get("risk_tier", "")
            if hasattr(risk_tier, "value"):
                risk_tier = risk_tier.value
            top_features = pred.get("top_features", [])
        else:
            customer_id = pred.customer_id
            churn_prob = pred.churn_probability
            risk_tier = pred.risk_tier.value
            top_features = pred.top_features

        parts = []
        for fc in top_features:
            if isinstance(fc, dict):
                feat = fc.get("feature", "")
                contrib = fc.get("contribution", 0)
            else:
                feat = fc.feature
                contrib = fc.contribution
            parts.append(f"{feat}={contrib}")
        top_feats = "; ".join(parts)

        rows.append({
            "customer_id": customer_id,
            "churn_probability": churn_prob,
            "risk_tier": risk_tier,
            "top_feature_contributions": top_feats,
        })

    df = pd.DataFrame(rows)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def _get_risk_tier(probability: float) -> RiskTier:
    if probability > 0.7:
        return RiskTier.high
    elif probability > 0.4:
        return RiskTier.medium
    return RiskTier.low
