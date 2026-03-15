"""Statistical pruning and three-layer leakage detection.

Pruning: removes zero-variance, high-null, and correlated features.
Leakage detection: statistical (AUC >0.90), temporal ordering, ablation test.
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def statistical_pruning(
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
) -> tuple[pd.DataFrame, dict]:
    """Remove noise features.

    Steps:
    1. Drop zero-variance features
    2. Drop features with >90% null
    3. Drop correlated features (|r| > 0.95, keep higher AUC)

    Returns:
        Pruned feature matrix, pruning report.
    """
    report = {"dropped": [], "original_count": len(feature_matrix.columns)}
    X = feature_matrix.copy()

    # Step 1: Zero variance
    stds = X.std()
    zero_var = stds[stds == 0].index.tolist()
    if zero_var:
        X = X.drop(columns=zero_var)
        report["dropped"].extend(
            [{"feature": f, "reason": "zero_variance"} for f in zero_var]
        )

    # Step 2: High null
    null_pct = X.isnull().mean()
    high_null = null_pct[null_pct > 0.90].index.tolist()
    if high_null:
        X = X.drop(columns=high_null)
        report["dropped"].extend(
            [{"feature": f, "reason": "high_null"} for f in high_null]
        )

    # Step 3: Correlation pruning
    if len(X.columns) > 1:
        X_filled = X.fillna(0)
        try:
            corr = X_filled.corr().abs()
            upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

            to_drop = set()
            for col in upper.columns:
                correlated = upper.index[upper[col] > 0.95].tolist()
                for corr_col in correlated:
                    if corr_col in to_drop or col in to_drop:
                        continue
                    auc_col = _safe_auc(X_filled[col], labels)
                    auc_corr = _safe_auc(X_filled[corr_col], labels)
                    drop = corr_col if auc_col >= auc_corr else col
                    to_drop.add(drop)
                    keep = col if drop == corr_col else corr_col
                    report["dropped"].append({
                        "feature": drop,
                        "reason": f"correlated_with_{keep}",
                    })

            if to_drop:
                X = X.drop(columns=list(to_drop))
        except Exception as e:
            logger.warning("Correlation pruning failed: %s", e)

    report["kept_count"] = len(X.columns)
    logger.info(
        "Pruning: %d → %d features (%d dropped)",
        report["original_count"], report["kept_count"], len(report["dropped"]),
    )

    return X, report


def leakage_detection(
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
    col_map: dict = None,
) -> tuple[pd.DataFrame, dict]:
    """Three-layer leakage detection.

    Layer 1: Statistical — flag features with univariate AUC > 0.90
    Layer 2: Temporal ordering — check if recency/frequency features
    Layer 3: Ablation test — train with/without suspect feature

    Returns:
        Cleaned feature matrix, leakage report.
    """
    report = {"suspects": [], "removed": [], "kept_as_leading": []}

    X = feature_matrix.fillna(0)

    # Layer 1: Statistical detection
    suspects = []
    for col in X.columns:
        auc = _safe_auc(X[col], labels)
        if auc > 0.90:
            suspects.append({"feature": col, "auc": round(auc, 3)})

    report["suspects"] = suspects

    if not suspects:
        return feature_matrix, report

    # Layer 2 + 3: Classify each suspect
    to_remove = []
    for suspect in suspects:
        feat_name = suspect["feature"]

        # Layer 2: Temporal ordering — recency and frequency features
        # are tautological with churn labels by construction
        is_recency = "_recency" in feat_name
        is_recent_freq = any(
            f"_frequency_{w}d" in feat_name for w in [30, 60, 90]
        )

        if is_recency:
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "tautological_with_churn_label",
                "auc": suspect["auc"],
            })
            continue

        if is_recent_freq:
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "overlaps_with_churn_definition",
                "auc": suspect["auc"],
            })
            continue

        # Layer 3: Ablation test
        drop_result = _ablation_test(X, labels, feat_name)

        if drop_result is None:
            # Ablation failed — remove conservatively
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "ablation_failed",
                "auc": suspect["auc"],
            })
        elif drop_result["auc_drop"] > 0.15:
            # Feature carries the model — suspicious
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "carries_model_single_feature",
                "auc": suspect["auc"],
                "auc_drop": drop_result["auc_drop"],
            })
        elif drop_result["auc_drop"] < 0.05:
            # Redundant — safe to remove
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "redundant_with_other_features",
                "auc": suspect["auc"],
                "auc_drop": drop_result["auc_drop"],
            })
        else:
            # Moderate impact — keep as potential leading indicator
            report["kept_as_leading"].append({
                "feature": feat_name,
                "auc": suspect["auc"],
                "auc_drop": drop_result["auc_drop"],
            })

    if to_remove:
        logger.info("Leakage detection removed %d features: %s", len(to_remove), to_remove)

    cleaned = feature_matrix.drop(columns=to_remove, errors="ignore")
    return cleaned, report


def _safe_auc(feature: pd.Series, labels: pd.Series) -> float:
    """Compute univariate AUC, return 0.5 on failure."""
    common = feature.dropna().index.intersection(labels.index)
    if len(common) < 20:
        return 0.5
    try:
        from sklearn.metrics import roc_auc_score
        y = labels[common].values
        if len(np.unique(y)) < 2:
            return 0.5
        return float(roc_auc_score(y, feature[common].values))
    except (ValueError, ImportError):
        return 0.5


def _ablation_test(
    X: pd.DataFrame,
    labels: pd.Series,
    feature_name: str,
) -> dict | None:
    """Train model with and without a feature, measure AUC drop."""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score
        import xgboost as xgb

        common = X.index.intersection(labels.index)
        if len(common) < 50:
            return None

        X_common = X.loc[common]
        y_common = labels.loc[common]

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_common, y_common, test_size=0.2, random_state=42, stratify=y_common,
        )

        params = dict(
            n_estimators=50, max_depth=4, verbosity=0,
            use_label_encoder=False, eval_metric="logloss",
        )

        # With feature
        model_with = xgb.XGBClassifier(**params)
        model_with.fit(X_tr, y_tr)
        auc_with = roc_auc_score(y_te, model_with.predict_proba(X_te)[:, 1])

        # Without feature
        X_tr_no = X_tr.drop(columns=[feature_name])
        X_te_no = X_te.drop(columns=[feature_name])
        model_without = xgb.XGBClassifier(**params)
        model_without.fit(X_tr_no, y_tr)
        auc_without = roc_auc_score(y_te, model_without.predict_proba(X_te_no)[:, 1])

        return {
            "auc_with": round(float(auc_with), 3),
            "auc_without": round(float(auc_without), 3),
            "auc_drop": round(float(auc_with - auc_without), 3),
        }

    except Exception as e:
        logger.warning("Ablation test failed for %s: %s", feature_name, e)
        return None
