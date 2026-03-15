"""Auto churn window selection.

Tests 6 candidate windows (30, 60, 90, 120, 180, 365 days),
trains a fast XGBoost for each, picks the one with best F1.
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CANDIDATE_WINDOWS = [30, 60, 90, 120, 180, 365]


def auto_select_churn_window(
    df: pd.DataFrame,
    feature_matrix: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
) -> dict:
    """Test 6 churn windows, return the one with best F1.

    Args:
        df: raw DataFrame
        feature_matrix: pre-computed per-customer features from field analysis
        customer_id_col: name of customer ID column
        date_col: name of transaction date column

    Returns:
        {
            "selected_window": int,
            "all_results": list of per-window results,
            "adaptive_gap": pd.Series (gap_vs_personal_median per customer),
        }
    """
    dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
    max_date = dates[dates.notna()].max()

    results = []

    for window in CANDIDATE_WINDOWS:
        cutoff = max_date - pd.Timedelta(days=window)

        # Generate labels
        last_purchase = df.assign(_dt=dates).groupby(customer_id_col)["_dt"].max()
        labels = (last_purchase < cutoff).astype(int)

        # Check churn rate
        churn_rate = float(labels.mean())
        if churn_rate < 0.05 or churn_rate > 0.80:
            results.append({
                "window": window,
                "f1": None,
                "churn_rate": round(churn_rate, 3),
                "status": "discarded",
                "reason": "churn_rate_out_of_range",
            })
            continue

        # Align feature matrix with labels
        common = feature_matrix.index.intersection(labels.index)
        if len(common) < 50:
            results.append({
                "window": window,
                "f1": None,
                "churn_rate": round(churn_rate, 3),
                "status": "discarded",
                "reason": "too_few_customers",
            })
            continue

        X = feature_matrix.loc[common].fillna(0)
        y = labels.loc[common]

        # Fast XGBoost — 50 trees, no tuning
        f1 = _train_fast_xgb(X, y)

        results.append({
            "window": window,
            "f1": round(f1, 3) if f1 is not None else None,
            "churn_rate": round(churn_rate, 3),
            "status": "tested",
        })

    # Pick best
    tested = [r for r in results if r.get("f1") is not None]
    if tested:
        best = max(tested, key=lambda r: r["f1"])
        selected = best["window"]
    else:
        selected = 90  # fallback
        logger.warning("No churn window produced usable results; defaulting to 90 days")

    # Compute adaptive gap feature
    adaptive_gap = _compute_adaptive_gap(df, customer_id_col, date_col, max_date)

    return {
        "selected_window": selected,
        "all_results": results,
        "adaptive_gap": adaptive_gap,
    }


def generate_labels(
    df: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
    window: int,
) -> pd.Series:
    """Generate binary churn labels for a given window.

    Returns:
        pd.Series indexed by customer_id, values 0 (active) or 1 (churned).
    """
    dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
    max_date = dates[dates.notna()].max()
    cutoff = max_date - pd.Timedelta(days=window)
    last_purchase = df.assign(_dt=dates).groupby(customer_id_col)["_dt"].max()
    return (last_purchase < cutoff).astype(int)


def _train_fast_xgb(X: pd.DataFrame, y: pd.Series) -> float | None:
    """Train a fast XGBoost and return F1 score."""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import f1_score
        import xgboost as xgb

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y,
        )

        n_pos = int((y_train == 1).sum())
        n_neg = int((y_train == 0).sum())
        spw = n_neg / max(n_pos, 1)

        model = xgb.XGBClassifier(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.1,
            scale_pos_weight=spw,
            use_label_encoder=False,
            eval_metric="logloss",
            verbosity=0,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        return float(f1_score(y_test, y_pred, zero_division=0))

    except Exception as e:
        logger.warning("Fast XGB training failed: %s", e)
        return None


def _compute_adaptive_gap(
    df: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
    max_date: pd.Timestamp,
) -> pd.Series:
    """Compute gap_vs_personal_median per customer.

    Value of 2.5 means the customer has been silent for 2.5x their normal interval.
    """
    dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
    df_valid = df[dates.notna()].assign(_dt=dates[dates.notna()])

    last_purchase = df_valid.groupby(customer_id_col)["_dt"].max()
    current_gap = (max_date - last_purchase).dt.days

    def median_gap(group):
        sorted_dates = group["_dt"].sort_values()
        if len(sorted_dates) < 2:
            return np.nan
        gaps = sorted_dates.diff().dt.days.dropna()
        return gaps.median() if len(gaps) > 0 else np.nan

    median_gaps = df_valid.groupby(customer_id_col).apply(
        median_gap, include_groups=False
    )

    # Avoid division by zero
    safe_median = median_gaps.replace(0, np.nan)
    adaptive = current_gap / safe_median

    return adaptive
