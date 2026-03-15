"""Tier 3 field interaction features.

Computes per-customer field visit features: visit frequency, duration,
order conversion, coverage.
"""
import numpy as np
import pandas as pd


def compute_field_features(
    df: pd.DataFrame, col_map: dict, customer_id_col: str
) -> pd.DataFrame:
    """Compute field interaction features grouped by customer.

    Expected roles in col_map: visit_id, visit_date, entity_type,
    visit_duration, order_booked, objective.
    """
    features = pd.DataFrame()

    visit_date_col = _find_col(col_map, "visit_date")
    duration_col = _find_col(col_map, "visit_duration")
    order_col = _find_col(col_map, "order_booked")
    objective_col = _find_col(col_map, "objective")
    entity_col = _find_col(col_map, "entity_type")

    grouped = df.groupby(customer_id_col)

    # Visit count
    features["visit_count"] = grouped.size()

    # Visit frequency
    if visit_date_col:
        try:
            dates = pd.to_datetime(df[visit_date_col])
            date_range = (dates.max() - dates.min()).days
            months = max(date_range / 30, 1)
            features["visits_per_month"] = features["visit_count"] / months

            # Recency
            max_date = dates.max()
            features["days_since_last_visit"] = (
                max_date - df.groupby(customer_id_col)[visit_date_col]
                .max()
                .apply(lambda x: pd.to_datetime(x))
            ).dt.days

            # Visit gap statistics
            features["visit_gap_mean"] = grouped.apply(
                lambda g: _compute_gap_mean(g, visit_date_col),
                include_groups=False,
            )
            features["visit_gap_std"] = grouped.apply(
                lambda g: _compute_gap_std(g, visit_date_col),
                include_groups=False,
            )

            # Visit frequency in last 30/60/90 days
            for window in [30, 60, 90]:
                cutoff = max_date - pd.Timedelta(days=window)
                features[f"visit_frequency_{window}d"] = (
                    df[dates > cutoff].groupby(customer_id_col).size()
                ).reindex(features.index, fill_value=0)

        except Exception:
            pass

    # Duration features
    if duration_col:
        dur_grouped = grouped[duration_col]
        features["visit_duration_mean"] = dur_grouped.mean()
        features["visit_duration_total"] = dur_grouped.sum()
        features["visit_duration_trend"] = grouped.apply(
            lambda g: _compute_trend(g[duration_col]),
            include_groups=False,
        )

    # Order conversion
    if order_col:
        try:
            # Handle both numeric and string values
            orders = pd.to_numeric(df[order_col], errors="coerce").fillna(0)
            df_temp = df.copy()
            df_temp["_order_numeric"] = orders
            order_grouped = df_temp.groupby(customer_id_col)["_order_numeric"]
            features["order_booked_total"] = order_grouped.sum()
            features["order_booked_mean"] = order_grouped.mean()
            features["visit_to_order_ratio"] = (
                features["order_booked_total"]
                / features["visit_count"].replace(0, np.nan)
            )
        except Exception:
            pass

    # Objective diversity
    if objective_col:
        features["objective_diversity"] = grouped[objective_col].nunique()

    # Entity type
    if entity_col:
        features["entity_type_diversity"] = grouped[entity_col].nunique()

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
        return float(dates.diff().dt.days.dropna().mean())
    except Exception:
        return 0.0


def _compute_gap_std(group: pd.DataFrame, date_col: str) -> float:
    try:
        dates = pd.to_datetime(group[date_col]).sort_values()
        if len(dates) < 3:
            return 0.0
        return float(dates.diff().dt.days.dropna().std())
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
