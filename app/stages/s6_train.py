from typing import Any
import time
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


def handle(session_id: str, session: dict[str, Any]) -> TrainResponse:
    features = session.get("labeled_features")
    labels = session.get("labels")

    if features is None or labels is None:
        raise HTTPException(
            status_code=400,
            detail="Label generation must be completed first.",
        )

    # Clean features: fill NaN, drop constant columns
    X = features.copy()
    X = X.fillna(0)

    # Drop columns with zero variance
    variance = X.var()
    constant_cols = variance[variance == 0].index.tolist()
    X = X.drop(columns=constant_cols)

    if X.shape[1] == 0:
        raise HTTPException(
            status_code=400,
            detail="No features with variance remain after cleaning.",
        )

    y = labels.loc[X.index]

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Train XGBoost
    start_time = time.time()

    # Handle class imbalance
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

    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    auc = round(float(roc_auc_score(y_test, y_proba)), 4)
    precision = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
    recall = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)

    cm = confusion_matrix(y_test, y_pred)
    cm_obj = ConfusionMatrix(
        true_negative=int(cm[0][0]),
        false_positive=int(cm[0][1]),
        false_negative=int(cm[1][0]),
        true_positive=int(cm[1][1]),
    )

    # Feature importance (top 10)
    importances = model.feature_importances_
    feat_names = X.columns.tolist()
    feat_imp = sorted(
        zip(feat_names, importances), key=lambda x: x[1], reverse=True
    )[:10]

    feature_importance = [
        FeatureImportance(feature=name, importance=round(float(imp), 4))
        for name, imp in feat_imp
    ]

    # Store model and test data for later stages
    store.update(session_id, {
        "stage": 6,
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "feature_names": feat_names,
        "metrics": {
            "auc": auc,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        },
        "confusion_matrix": cm_obj.model_dump(),
        "feature_importance": [fi.model_dump() for fi in feature_importance],
        "training_time_seconds": training_time,
    })

    return TrainResponse(
        metrics={"auc": auc, "precision": precision, "recall": recall, "f1": f1},
        confusion_matrix=cm_obj,
        feature_importance=feature_importance,
        training_time_seconds=training_time,
    )
