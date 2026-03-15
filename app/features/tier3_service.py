"""Tier 3 service/warranty features.

Computes per-customer service features from service/complaint data:
ticket frequency, resolution time, satisfaction scores.
"""
import numpy as np
import pandas as pd


def compute_service_features(
    df: pd.DataFrame, col_map: dict, customer_id_col: str
) -> pd.DataFrame:
    """Compute service features grouped by customer.

    Expected roles in col_map: ticket_id, ticket_date, resolution_date,
    complaint_category, warranty_status, csat_score, tat_days.
    """
    features = pd.DataFrame()

    ticket_date_col = _find_col(col_map, "ticket_date")
    resolution_col = _find_col(col_map, "resolution_date")
    complaint_col = _find_col(col_map, "complaint_category")
    warranty_col = _find_col(col_map, "warranty_status")
    csat_col = _find_col(col_map, "csat_score")
    tat_col = _find_col(col_map, "tat_days")

    grouped = df.groupby(customer_id_col)

    # Ticket count
    features["ticket_count"] = grouped.size()

    # Ticket frequency (per month)
    if ticket_date_col:
        try:
            dates = pd.to_datetime(df[ticket_date_col])
            date_range = (dates.max() - dates.min()).days
            months = max(date_range / 30, 1)
            features["tickets_per_month"] = features["ticket_count"] / months
        except Exception:
            pass

    # Resolution time features
    if ticket_date_col and resolution_col:
        try:
            df_copy = df.copy()
            df_copy["_tat"] = (
                pd.to_datetime(df_copy[resolution_col])
                - pd.to_datetime(df_copy[ticket_date_col])
            ).dt.days
            tat_grouped = df_copy.groupby(customer_id_col)["_tat"]
            features["resolution_time_mean"] = tat_grouped.mean()
            features["resolution_time_max"] = tat_grouped.max()
            features["resolution_time_std"] = tat_grouped.std().fillna(0)
        except Exception:
            pass

    # TAT features (if provided directly)
    if tat_col:
        tat_grouped = grouped[tat_col]
        features["tat_mean"] = tat_grouped.mean()
        features["tat_max"] = tat_grouped.max()

    # CSAT features
    if csat_col:
        csat_grouped = grouped[csat_col]
        features["csat_mean"] = csat_grouped.mean()
        features["csat_min"] = csat_grouped.min()
        features["csat_std"] = csat_grouped.std().fillna(0)
        features["csat_trend"] = grouped.apply(
            lambda g: _compute_trend(g[csat_col]), include_groups=False,
        )

    # Complaint category diversity
    if complaint_col:
        features["complaint_category_diversity"] = grouped[complaint_col].nunique()

    # Warranty status
    if warranty_col:
        features["warranty_active_count"] = grouped[warranty_col].apply(
            lambda x: (x.str.lower().isin(["active", "valid", "yes", "1"])).sum()
        )

    # Recency of last ticket
    if ticket_date_col:
        try:
            dates = pd.to_datetime(df[ticket_date_col])
            max_date = dates.max()
            features["days_since_last_ticket"] = (
                max_date - df.groupby(customer_id_col)[ticket_date_col]
                .max()
                .apply(lambda x: pd.to_datetime(x))
            ).dt.days
        except Exception:
            pass

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
