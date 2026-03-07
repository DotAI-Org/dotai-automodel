from typing import Any
import pandas as pd
import numpy as np
from fastapi import HTTPException

from app.session_store import store


def handle(session_id: str, session: dict[str, Any]) -> dict:
    df = session.get("dataframe")
    col_map = session.get("col_map")
    feature_matrix = session.get("feature_matrix")
    mcq_answers = session.get("mcq_answers", {})

    if df is None or col_map is None or feature_matrix is None:
        raise HTTPException(
            status_code=400,
            detail="Feature engineering must be completed first.",
        )

    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    dates = pd.to_datetime(df[date_col])

    # Use churn window from stage 4 if available, otherwise compute
    churn_window_days = session.get("churn_window_days") or _get_churn_window(df, col_map, mcq_answers)

    max_date = dates.max()
    cutoff_date = max_date - pd.Timedelta(days=churn_window_days)

    # Recompute features as of cutoff date
    df_before = df[dates <= cutoff_date].copy()

    if len(df_before) == 0:
        raise HTTPException(
            status_code=400,
            detail="Not enough data before cutoff date. Try a shorter churn window.",
        )

    # Label: 1 if no purchase after cutoff, 0 otherwise
    df_after = df[dates > cutoff_date].copy()
    customers_after = set(df_after[cust_col].unique())
    all_customers = set(df_before[cust_col].unique())

    labels = pd.Series(
        {cid: 1 if cid not in customers_after else 0 for cid in all_customers},
        name="churn_label",
    )

    # Align feature matrix with label customers
    common_customers = feature_matrix.index.intersection(labels.index)
    if len(common_customers) == 0:
        raise HTTPException(
            status_code=400,
            detail="No overlap between feature matrix and label customers.",
        )

    aligned_features = feature_matrix.loc[common_customers]
    aligned_labels = labels.loc[common_customers]

    churned_count = int(aligned_labels.sum())
    active_count = int(len(aligned_labels) - churned_count)
    churn_rate = round(churned_count / len(aligned_labels), 4) if len(aligned_labels) > 0 else 0

    store.update(session_id, {
        "stage": 5,
        "labels": aligned_labels,
        "labeled_features": aligned_features,
        "churn_window_days": churn_window_days,
        "cutoff_date": str(cutoff_date.date()),
    })

    return {
        "churn_rate": churn_rate,
        "churned_count": churned_count,
        "active_count": active_count,
        "churn_window_days": churn_window_days,
        "cutoff_date": str(cutoff_date.date()),
    }


def _assign_labels(
    df: pd.DataFrame, col_map: dict, cutoff_date: pd.Timestamp
) -> pd.Series:
    """Assign churn labels: 1 if no purchase after cutoff, 0 otherwise."""
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    dates = pd.to_datetime(df[date_col])

    df_before = df[dates <= cutoff_date]
    df_after = df[dates > cutoff_date]

    customers_after = set(df_after[cust_col].unique())
    all_customers = set(df_before[cust_col].unique())

    return pd.Series(
        {cid: 1 if cid not in customers_after else 0 for cid in all_customers},
        name="churn_label",
    )


def _get_churn_window(df: pd.DataFrame, col_map: dict, mcq_answers: dict) -> int:
    # Check if user provided churn window via MCQ
    for key, value in mcq_answers.items():
        if "churn" in key.lower() or "inactive" in key.lower():
            try:
                days = int(value)
                if 7 <= days <= 365:
                    return days
            except (ValueError, TypeError):
                pass

    # Auto-derive: 2x median inter-purchase interval
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    def _median_gap(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 2:
            return np.nan
        return dates.diff().dt.days.dropna().median()

    gaps = df.groupby(cust_col).apply(_median_gap).dropna()
    if len(gaps) == 0:
        return 90  # default fallback

    median_gap = gaps.median()
    churn_window = int(median_gap * 2)

    # Clamp to reasonable range
    return max(14, min(churn_window, 365))
