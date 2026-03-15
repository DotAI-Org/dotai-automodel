"""Tier 3 loyalty/membership features.

Computes per-customer loyalty features from loyalty program data:
points activity, tier status, engagement patterns.
"""
import numpy as np
import pandas as pd


def compute_loyalty_features(
    df: pd.DataFrame, col_map: dict, customer_id_col: str
) -> pd.DataFrame:
    """Compute loyalty features grouped by customer.

    Expected roles in col_map: points_earned, points_redeemed, tier,
    enrollment_date, transaction_type, member_id.
    """
    features = pd.DataFrame()

    points_earned_col = _find_col(col_map, "points_earned")
    points_redeemed_col = _find_col(col_map, "points_redeemed")
    tier_col = _find_col(col_map, "tier")
    enrollment_col = _find_col(col_map, "enrollment_date")
    txn_type_col = _find_col(col_map, "transaction_type")

    grouped = df.groupby(customer_id_col)

    # Points earned features
    if points_earned_col:
        earned = grouped[points_earned_col]
        features["points_earned_total"] = earned.sum()
        features["points_earned_mean"] = earned.mean()
        features["points_earned_std"] = earned.std().fillna(0)
        features["points_earned_max"] = earned.max()
        features["points_earned_trend"] = grouped.apply(
            lambda g: _compute_trend(g[points_earned_col]), include_groups=False,
        )

    # Points redeemed features
    if points_redeemed_col:
        redeemed = grouped[points_redeemed_col]
        features["points_redeemed_total"] = redeemed.sum()
        features["points_redeemed_mean"] = redeemed.mean()

        # Redemption ratio
        if points_earned_col:
            total_earned = grouped[points_earned_col].sum()
            total_redeemed = redeemed.sum()
            features["redemption_ratio"] = (
                total_redeemed / total_earned.replace(0, np.nan)
            )

    # Tier features
    if tier_col:
        features["tier_diversity"] = grouped[tier_col].nunique()
        features["tier_latest"] = grouped[tier_col].last()

    # Enrollment tenure
    if enrollment_col:
        try:
            enroll_dates = pd.to_datetime(df[enrollment_col])
            max_date = enroll_dates.max()
            features["enrollment_tenure_days"] = (
                max_date - df.groupby(customer_id_col)[enrollment_col]
                .first()
                .apply(lambda x: pd.to_datetime(x))
            ).dt.days
        except Exception:
            pass

    # Transaction type diversity
    if txn_type_col:
        features["txn_type_diversity"] = grouped[txn_type_col].nunique()
        features["txn_type_count"] = grouped[txn_type_col].count()

    # Engagement frequency (transactions per month)
    features["loyalty_txn_count"] = grouped.size()

    return features


def _find_col(col_map: dict, role: str) -> str | None:
    """Find column name for a given role."""
    for col_name, col_role in col_map.items():
        if col_role == role:
            return col_name
    return None


def _compute_trend(series: pd.Series) -> float:
    """Compute linear trend slope, normalized."""
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
