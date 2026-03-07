import time
import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

logger = logging.getLogger(__name__)


@dataclass
class ModelResult:
    name: str
    model: Any
    metrics: dict  # {auc, precision, recall, f1}
    confusion_matrix: dict  # {TP, FP, TN, FN}
    feature_importance: list[dict]  # [{feature, importance}]
    training_time: float
    feature_names: list[str] = field(default_factory=list)


def prepare_data(
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, list[str]]:
    """Clean features and split into train/test. Returns X_train, X_test, y_train, y_test, feature_names."""
    X = feature_matrix.copy()
    X = X.fillna(0)

    # Drop columns with zero variance
    variance = X.var()
    constant_cols = variance[variance == 0].index.tolist()
    X = X.drop(columns=constant_cols)

    if X.shape[1] == 0:
        raise ValueError("No features with variance remain after cleaning.")

    y = labels.loc[X.index]
    feature_names = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    return X_train, X_test, y_train, y_test, feature_names


def _evaluate_model(model, X_test, y_test, feature_names: list[str]) -> tuple[dict, dict, list[dict]]:
    """Compute metrics, confusion matrix, and feature importance for a fitted model."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
    }

    cm = confusion_matrix(y_test, y_pred)
    cm_dict = {
        "TN": int(cm[0][0]),
        "FP": int(cm[0][1]),
        "FN": int(cm[1][0]),
        "TP": int(cm[1][1]),
    }

    importances = model.feature_importances_
    feat_imp = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )
    feature_importance = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in feat_imp
    ]

    return metrics, cm_dict, feature_importance


def _train_xgboost(X_train, y_train, X_test, y_test, feature_names: list[str]) -> ModelResult:
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

    start = time.time()
    model.fit(X_train, y_train)
    training_time = round(time.time() - start, 2)

    metrics, cm_dict, feature_importance = _evaluate_model(model, X_test, y_test, feature_names)

    return ModelResult(
        name="xgboost",
        model=model,
        metrics=metrics,
        confusion_matrix=cm_dict,
        feature_importance=feature_importance,
        training_time=training_time,
        feature_names=feature_names,
    )


def _train_random_forest(X_train, y_train, X_test, y_test, feature_names: list[str]) -> ModelResult:
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        class_weight="balanced",
        random_state=42,
    )

    start = time.time()
    model.fit(X_train, y_train)
    training_time = round(time.time() - start, 2)

    metrics, cm_dict, feature_importance = _evaluate_model(model, X_test, y_test, feature_names)

    return ModelResult(
        name="random_forest",
        model=model,
        metrics=metrics,
        confusion_matrix=cm_dict,
        feature_importance=feature_importance,
        training_time=training_time,
        feature_names=feature_names,
    )


def train_all_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    feature_names: list[str],
) -> list[ModelResult]:
    """Train XGBoost and Random Forest on the same split. Returns list sorted by AUC descending."""
    results = []

    try:
        xgb_result = _train_xgboost(X_train, y_train, X_test, y_test, feature_names)
        results.append(xgb_result)
    except Exception as e:
        logger.error(f"XGBoost training failed: {e}")

    try:
        rf_result = _train_random_forest(X_train, y_train, X_test, y_test, feature_names)
        results.append(rf_result)
    except Exception as e:
        logger.error(f"Random Forest training failed: {e}")

    from app.agent.scoring import composite_score
    results.sort(key=lambda r: composite_score(r.metrics), reverse=True)
    return results
