"""Tier 3 returns/delivery features.

Computes per-customer returns features: return frequency, reasons, patterns.
"""
import numpy as np
import pandas as pd


def compute_returns_features(
    df: pd.DataFrame, col_map: dict, customer_id_col: str
) -> pd.DataFrame:
    """Compute returns features grouped by customer.

    Expected roles in col_map: return_id, return_date, return_reason,
    return_quantity, original_invoice.
    """
    features = pd.DataFrame()

    return_date_col = _find_col(col_map, "return_date")
    return_reason_col = _find_col(col_map, "return_reason")
    return_qty_col = _find_col(col_map, "return_quantity")

    grouped = df.groupby(customer_id_col)

    # Return count
    features["return_count"] = grouped.size()

    # Return quantity features
    if return_qty_col:
        qty_grouped = grouped[return_qty_col]
        features["return_qty_total"] = qty_grouped.sum()
        features["return_qty_mean"] = qty_grouped.mean()
        features["return_qty_max"] = qty_grouped.max()

    # Return reason diversity
    if return_reason_col:
        features["return_reason_diversity"] = grouped[return_reason_col].nunique()
        # Most common reason per customer
        features["return_reason_mode"] = grouped[return_reason_col].agg(
            lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "unknown"
        )

    # Return frequency
    if return_date_col:
        try:
            dates = pd.to_datetime(df[return_date_col])
            date_range = (dates.max() - dates.min()).days
            months = max(date_range / 30, 1)
            features["returns_per_month"] = features["return_count"] / months

            # Recency of last return
            max_date = dates.max()
            features["days_since_last_return"] = (
                max_date - df.groupby(customer_id_col)[return_date_col]
                .max()
                .apply(lambda x: pd.to_datetime(x))
            ).dt.days

            # Return gap statistics
            features["return_gap_mean"] = grouped.apply(
                lambda g: _compute_gap_mean(g, return_date_col),
                include_groups=False,
            )
        except Exception:
            pass

    # Return trend
    if return_date_col and return_qty_col:
        features["return_qty_trend"] = grouped.apply(
            lambda g: _compute_trend(g[return_qty_col]),
            include_groups=False,
        )

    return features


def _find_col(col_map: dict, role: str) -> str | None:
    for col_name, col_role in col_map.items():
        if col_role == role:
            return col_name
    return None


def _compute_gap_mean(group: pd.DataFrame, date_col: str) -> float:
    try:
        dates = pd.to_datetime(group[date_col]).sort_values()
        if len(dates) < 2:
            return 0.0
        gaps = dates.diff().dt.days.dropna()
        return float(gaps.mean())
    except Exception:
        return 0.0


def _compute_trend(series: pd.Series) -> float:
    if len(series) < 3:
        return 0.0
    try:
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values.astype(float), 1)[0]
        mean = series.mean()
        if mean != 0:
            return float(slope / abs(mean))
        return float(slope)
    except Exception:
        return 0.0
