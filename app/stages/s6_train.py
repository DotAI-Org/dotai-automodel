"""Stage 6: Multi-model training with tier-based feature grouping."""
import logging
import time
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
import xgboost as xgb

from app.session_store import store
from app.models.schemas import (
    TrainResponse,
    ConfusionMatrix,
    FeatureImportance,
)

logger = logging.getLogger(__name__)


def handle(session_id: str, session: dict[str, Any]) -> TrainResponse:
    """Train Model A (baseline) + Model B (enriched) + applicable C/D/E."""
    features = session.get("labeled_features")
    labels = session.get("labels")

    if features is None or labels is None:
        raise HTTPException(
            status_code=400,
            detail="Label generation must be completed first.",
        )

    tier_map = session.get("feature_tier_map", {})
    detected_types = session.get("detected_data_types", [1])

    # Check if exhaustive analysis was done (multi-model path)
    has_exhaustive = session.get("field_analysis_signature") is not None

    if not has_exhaustive:
        # Legacy single-model path
        return _handle_legacy(session_id, session, features, labels)

    start_time = time.time()
    results = {}

    # Model A: Transaction-only (Tier 1 + Tier 2)
    tier12_cols = [c for c in features.columns if tier_map.get(c, 4) <= 2]
    if tier12_cols:
        result_a = _train_single(features[tier12_cols], labels, "Model A (transactions)")
        if result_a:
            results["model_a"] = result_a

    # Model B: Enriched (all tiers)
    result_b = _train_single(features, labels, "Model B (enriched)")
    if result_b:
        results["model_b"] = result_b

    # Model C: Engagement churn (Type 3 or 5 — loyalty/field data)
    if 3 in detected_types or 5 in detected_types:
        tier3_cols = [c for c in features.columns if tier_map.get(c, 4) == 3]
        if len(tier3_cols) >= 3:
            result_c = _train_single(
                features[tier3_cols], labels, "Model C (engagement risk)"
            )
            if result_c:
                results["model_c"] = result_c

    # Model D: Influencer propagation (Type 3 with influencer features)
    if 3 in detected_types and "influencer_features" in session:
        inf_features = session["influencer_features"]
        if len(inf_features.columns) >= 3:
            result_d = _train_single(
                inf_features.reindex(labels.index).fillna(0),
                labels,
                "Model D (influencer signals)",
            )
            if result_d:
                results["model_d"] = result_d

    # Model E: Service-driven (Type 2)
    if 2 in detected_types:
        service_cols = [
            c for c in features.columns if tier_map.get(c, 4) in (1, 2, 3)
        ]
        if service_cols:
            result_e = _train_single(
                features[service_cols], labels, "Model E (service-driven)"
            )
            if result_e:
                results["model_e"] = result_e

    if not results:
        raise HTTPException(
            status_code=400,
            detail="No models could be trained. Check feature matrix.",
        )

    # Select champion (highest F1 among A and B)
    ab_results = [r for k, r in results.items() if k in ("model_a", "model_b")]
    if ab_results:
        champion = max(ab_results, key=lambda r: r["metrics"]["f1"])
    else:
        champion = list(results.values())[0]

    # Compute lift (Model A vs Model B)
    lift = None
    if "model_a" in results and "model_b" in results:
        lift = {
            "f1_baseline": results["model_a"]["metrics"]["f1"],
            "f1_enriched": results["model_b"]["metrics"]["f1"],
            "f1_lift": round(
                results["model_b"]["metrics"]["f1"]
                - results["model_a"]["metrics"]["f1"],
                3,
            ),
        }

    # Feature group attribution
    attribution = _compute_tier_attribution(champion, tier_map)

    training_time = round(time.time() - start_time, 2)

    # Build confusion matrix and feature importance for response
    cm = champion["confusion_matrix"]
    cm_obj = ConfusionMatrix(
        true_negative=int(cm[0][0]),
        false_positive=int(cm[0][1]),
        false_negative=int(cm[1][0]),
        true_positive=int(cm[1][1]),
    )

    feature_importance = [
        FeatureImportance(feature=name, importance=round(float(imp), 4))
        for name, imp in list(champion["feature_importance"].items())[:10]
    ]

    # Build serializable model comparison (without model objects)
    model_comparison_serializable = {}
    for k, v in results.items():
        model_comparison_serializable[k] = {
            "name": v["name"],
            "metrics": v["metrics"],
            "feature_importance": v["feature_importance"],
        }

    store.update(session_id, {
        "stage": 6,
        "model": champion["model"],
        "X_test": champion["X_test"],
        "y_test": champion["y_test"],
        "feature_names": champion["feature_names"],
        "metrics": champion["metrics"],
        "confusion_matrix": cm_obj.model_dump(),
        "feature_importance": [fi.model_dump() for fi in feature_importance],
        "training_time_seconds": training_time,
        "model_comparison": model_comparison_serializable,
        "champion_name": champion["name"],
        "lift": lift,
        "tier_attribution": attribution,
        "models_trained": list(results.keys()),
    })

    return TrainResponse(
        metrics=champion["metrics"],
        confusion_matrix=cm_obj,
        feature_importance=feature_importance,
        training_time_seconds=training_time,
        champion_name=champion["name"],
        lift=lift,
        models_trained=list(results.keys()),
        tier_attribution=attribution,
    )


def _handle_legacy(
    session_id: str,
    session: dict,
    features: pd.DataFrame,
    labels: pd.Series,
) -> TrainResponse:
    """Legacy single-model training path."""
    X = features.copy().fillna(0)

    # Drop zero-variance columns
    variance = X.var()
    constant_cols = variance[variance == 0].index.tolist()
    X = X.drop(columns=constant_cols)

    if X.shape[1] == 0:
        raise HTTPException(
            status_code=400,
            detail="No features with variance remain after cleaning.",
        )

    y = labels.loc[X.index]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    start_time = time.time()

    n_pos = y_train.sum()
    n_neg = len(y_train) - n_pos
    scale_pos_weight = n_neg / max(n_pos, 1)

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    training_time = round(time.time() - start_time, 2)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    auc = round(float(roc_auc_score(y_test, y_proba)), 4)
    precision = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
    recall = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
    f1_val = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)

    cm = confusion_matrix(y_test, y_pred)
    cm_obj = ConfusionMatrix(
        true_negative=int(cm[0][0]),
        false_positive=int(cm[0][1]),
        false_negative=int(cm[1][0]),
        true_positive=int(cm[1][1]),
    )

    importances = model.feature_importances_
    feat_names = X.columns.tolist()
    feat_imp = sorted(
        zip(feat_names, importances), key=lambda x: x[1], reverse=True
    )[:10]

    feature_importance = [
        FeatureImportance(feature=name, importance=round(float(imp), 4))
        for name, imp in feat_imp
    ]

    store.update(session_id, {
        "stage": 6,
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "feature_names": feat_names,
        "metrics": {
            "auc": auc, "precision": precision, "recall": recall, "f1": f1_val,
        },
        "confusion_matrix": cm_obj.model_dump(),
        "feature_importance": [fi.model_dump() for fi in feature_importance],
        "training_time_seconds": training_time,
    })

    return TrainResponse(
        metrics={"auc": auc, "precision": precision, "recall": recall, "f1": f1_val},
        confusion_matrix=cm_obj,
        feature_importance=feature_importance,
        training_time_seconds=training_time,
    )


def _train_single(
    X: pd.DataFrame, y: pd.Series, name: str
) -> dict | None:
    """Train a single XGBoost model with the given features and labels."""
    try:
        X = X.fillna(0)

        # Align indices
        common = X.index.intersection(y.index)
        if len(common) < 50:
            logger.warning("Skipping %s: only %d samples", name, len(common))
            return None

        X = X.loc[common]
        y_aligned = y.loc[common]

        # Drop zero-variance
        stds = X.std()
        non_zero_var = stds[stds > 0].index.tolist()
        X = X[non_zero_var]

        if X.shape[1] == 0:
            logger.warning("Skipping %s: no features with variance", name)
            return None

        # Check class balance
        n_classes = y_aligned.nunique()
        if n_classes < 2:
            logger.warning("Skipping %s: only one class present", name)
            return None

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_aligned, test_size=0.2, random_state=42, stratify=y_aligned
        )

        n_pos = int(y_train.sum())
        n_neg = len(y_train) - n_pos
        scale_pos_weight = n_neg / max(n_pos, 1)

        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            verbosity=0,
            random_state=42,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics = {
            "auc": round(float(roc_auc_score(y_test, y_prob)), 3),
            "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 3),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 3),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 3),
        }

        importance = dict(zip(X.columns, model.feature_importances_))
        importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        cm = confusion_matrix(y_test, y_pred)

        logger.info(
            "%s: AUC=%.3f, F1=%.3f, %d features",
            name, metrics["auc"], metrics["f1"], X.shape[1],
        )

        return {
            "name": name,
            "model": model,
            "metrics": metrics,
            "feature_importance": importance,
            "feature_names": list(X.columns),
            "X_test": X_test,
            "y_test": y_test,
            "confusion_matrix": cm.tolist(),
        }

    except Exception as e:
        logger.warning("Training failed for %s: %s", name, e)
        return None


def _compute_tier_attribution(champion: dict, tier_map: dict) -> dict:
    """Group feature importance by tier."""
    attribution = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    for feat, importance in champion["feature_importance"].items():
        tier = tier_map.get(feat, 4)
        attribution[tier] += importance

    total = sum(attribution.values()) or 1
    return {
        f"tier_{k}": round(v / total * 100, 1)
        for k, v in attribution.items()
    }
