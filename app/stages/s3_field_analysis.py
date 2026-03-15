"""Exhaustive field analysis engine.

Runs 4 analyses per field based on dtype (numeric, categorical, datetime).
One pass produces both the data signature report (for LLM hypothesis)
and the per-customer feature matrix (for training).
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def analyze_all_fields(
    df: pd.DataFrame,
    col_map: dict,
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,
) -> tuple[dict, pd.DataFrame]:
    """Run 4 analyses per field based on dtype.

    Args:
        df: raw DataFrame
        col_map: {column_name: role} mapping from Stage 2
        customer_id_col: name of the customer ID column
        date_col: name of the primary date column (for trend computation)
        labels: optional churn labels (for univariate signal analysis)

    Returns:
        signature: dict of per-field statistics
        feature_matrix: DataFrame indexed by customer_id
    """
    signature = {}
    all_features = {}

    for col_name, role in col_map.items():
        if col_name == customer_id_col:
            continue
        if col_name not in df.columns:
            continue
        # Skip pandas artifact columns
        if col_name.lower().strip().startswith("unnamed"):
            logger.info("Skipping unnamed column: %s", col_name)
            continue
        # Skip auto-increment columns: numeric, high cardinality, monotonically increasing
        if _is_auto_increment(df[col_name]):
            logger.info("Skipping auto-increment column: %s", col_name)
            continue

        dtype = _infer_analysis_dtype(df[col_name])

        try:
            if dtype == "numeric":
                sig, feats = analyze_numeric(
                    df, col_name, customer_id_col, date_col, labels
                )
            elif dtype == "categorical":
                sig, feats = analyze_categorical(
                    df, col_name, customer_id_col, date_col, labels
                )
            elif dtype == "datetime":
                sig, feats = analyze_datetime(df, col_name, customer_id_col)
            else:
                sig = {"dtype": "text", "cardinality": int(df[col_name].nunique())}
                feats = {}
        except Exception as e:
            logger.warning("Field analysis failed for %s: %s", col_name, e)
            sig = {"dtype": dtype, "error": str(e)}
            feats = {}

        signature[col_name] = {**sig, "role": role}
        all_features.update(feats)

    # Build feature matrix
    if all_features:
        feature_matrix = pd.DataFrame(all_features)
        feature_matrix.index.name = "customer_id"
    else:
        feature_matrix = pd.DataFrame()

    return signature, feature_matrix


def analyze_numeric(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a numeric field.

    1. Distribution (signature only)
    2. Per-customer profile (signature + features)
    3. Univariate churn signal (signature only)
    4. Temporal trend (feature)
    """
    col = pd.to_numeric(df[col_name], errors="coerce")
    features = {}

    # Analysis 1: Distribution
    sig = {
        "dtype": "numeric",
        "mean": _safe_float(col.mean()),
        "median": _safe_float(col.median()),
        "std": _safe_float(col.std()),
        "skew": _safe_float(col.skew()),
        "p25": _safe_float(col.quantile(0.25)),
        "p75": _safe_float(col.quantile(0.75)),
    }
    std_val = col.std()
    if std_val and std_val > 0:
        sig["outlier_pct"] = _safe_float(
            (np.abs(col - col.mean()) > 3 * std_val).mean() * 100
        )

    # Analysis 2: Per-customer profile
    grouped = df.assign(**{col_name: col}).groupby(customer_id_col)[col_name]
    per_cust_mean = grouped.mean()
    per_cust_std = grouped.std().fillna(0)

    features[f"{col_name}_mean"] = per_cust_mean
    features[f"{col_name}_std"] = per_cust_std

    sig["per_customer_mean_of_means"] = _safe_float(per_cust_mean.mean())
    sig["per_customer_std_of_means"] = _safe_float(per_cust_mean.std())

    # Analysis 3: Univariate churn signal
    if labels is not None:
        auc = _compute_univariate_auc(per_cust_mean, labels)
        if auc is not None:
            sig["univariate_churn_auc"] = auc

    # Analysis 4: Temporal trend
    if date_col and date_col in df.columns:
        trend = _compute_trend(df, col_name, customer_id_col, date_col, numeric_col=col)
        if trend is not None:
            features[f"{col_name}_trend"] = trend
            sig["trend_direction"] = "increasing" if trend.mean() > 0 else "decreasing"

    return sig, features


def analyze_categorical(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a categorical field.

    1. Concentration (signature only)
    2. Per-customer diversity (feature)
    3. Churn rate by value (feature)
    4. Temporal shift (feature)
    """
    features = {}

    # Analysis 1: Concentration
    vc = df[col_name].value_counts(normalize=True).head(5)
    sig = {
        "dtype": "categorical",
        "top_5": {str(k): round(float(v) * 100, 1) for k, v in vc.items()},
        "unique_count": int(df[col_name].nunique()),
        "long_tail_pct": round(float(1 - vc.sum()) * 100, 1),
    }

    # Analysis 2: Per-customer diversity
    diversity = df.groupby(customer_id_col)[col_name].nunique()
    features[f"{col_name}_diversity"] = diversity
    sig["avg_diversity_per_customer"] = _safe_float(diversity.mean())

    # Analysis 3: Churn rate by value
    if labels is not None:
        mode_per_customer = df.groupby(customer_id_col)[col_name].agg(
            lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None
        )
        value_churn_rates = {}
        for val in df[col_name].dropna().unique():
            customers_with_val = mode_per_customer[mode_per_customer == val].index
            common = customers_with_val.intersection(labels.index)
            if len(common) >= 5:
                value_churn_rates[str(val)] = round(float(labels[common].mean()), 3)

        sig["churn_rate_by_value"] = value_churn_rates

        if value_churn_rates:
            churn_rate_map = value_churn_rates
            features[f"{col_name}_churn_rate"] = mode_per_customer.map(
                lambda x: churn_rate_map.get(str(x), 0)
            )

    # Analysis 4: Temporal shift (Jaccard distance between 1st and 2nd half)
    if date_col and date_col in df.columns:
        shift = _compute_categorical_shift(df, col_name, customer_id_col, date_col)
        if shift is not None:
            features[f"{col_name}_shift"] = shift

    return sig, features


def analyze_datetime(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a datetime field.

    1. Recency (feature)
    2. Frequency (feature)
    3. Gap profile (feature)
    4. Seasonality (signature only)
    """
    features = {}
    dates = pd.to_datetime(df[col_name], format="mixed", dayfirst=True)
    valid_mask = dates.notna()

    if valid_mask.sum() < 2:
        return {"dtype": "datetime", "valid_count": int(valid_mask.sum())}, {}

    max_date = dates[valid_mask].max()

    # Analysis 1: Recency
    df_valid = df[valid_mask].assign(_dt=dates[valid_mask])
    last_per_customer = df_valid.groupby(customer_id_col)["_dt"].max()
    recency = (max_date - last_per_customer).dt.days
    features[f"{col_name}_recency"] = recency

    sig = {
        "dtype": "datetime",
        "min": str(dates[valid_mask].min()),
        "max": str(max_date),
        "recency_median": _safe_float(recency.median()),
        "recency_p25": _safe_float(recency.quantile(0.25)),
        "recency_p75": _safe_float(recency.quantile(0.75)),
    }

    # Analysis 2: Frequency
    for window_days in [30, 60, 90]:
        cutoff = max_date - pd.Timedelta(days=window_days)
        freq = df_valid[df_valid["_dt"] >= cutoff].groupby(customer_id_col).size()
        freq = freq.reindex(last_per_customer.index, fill_value=0)
        features[f"{col_name}_frequency_{window_days}d"] = freq

    sig["frequency_30d_median"] = _safe_float(
        features.get(f"{col_name}_frequency_30d", pd.Series([0])).median()
    )

    # Analysis 3: Gap profile
    gap_stats = _compute_gap_profile(df_valid, col_name, customer_id_col)
    if gap_stats is not None:
        for stat_name, stat_series in gap_stats.items():
            features[f"{col_name}_{stat_name}"] = stat_series
        sig["gap_median"] = _safe_float(
            gap_stats.get("gap_avg", pd.Series([0])).median()
        )

    # Analysis 4: Seasonality
    monthly = dates[valid_mask].dt.month.value_counts().sort_index()
    avg_monthly = monthly.mean()
    if avg_monthly > 0:
        seasonal_index = (monthly / avg_monthly).to_dict()
        sig["seasonal_index"] = {
            str(k): round(float(v), 2) for k, v in seasonal_index.items()
        }
        sig["is_seasonal"] = any(
            v > 1.3 or v < 0.7 for v in seasonal_index.values()
        )

    return sig, features


def analyze_cross_file(
    df_primary: pd.DataFrame,
    df_secondary: pd.DataFrame,
    primary_customer_col: str,
    secondary_customer_col: str,
    secondary_file_type: str,
) -> tuple[dict, dict]:
    """Compute cross-file overlap statistics."""
    primary_customers = set(df_primary[primary_customer_col].unique())
    secondary_customers = set(df_secondary[secondary_customer_col].unique())
    overlap = primary_customers & secondary_customers

    sig = {
        "overlap_rate": round(
            len(overlap) / max(len(primary_customers), 1) * 100, 1
        ),
        "overlap_count": len(overlap),
        "primary_count": len(primary_customers),
        "secondary_count": len(secondary_customers),
        "secondary_type": secondary_file_type,
    }

    return sig, {}


# --- Helpers ---

def _is_auto_increment(series: pd.Series) -> bool:
    """Detect auto-incrementing integer columns (row IDs, transaction IDs, etc.).

    Handles both per-row unique IDs and transaction-level IDs that repeat
    across line items. Checks deduplicated values for: numeric, integer-valued,
    and mostly monotonically increasing (>90% of consecutive diffs are positive).
    """
    if not pd.api.types.is_numeric_dtype(series):
        return False
    clean = series.dropna()
    if len(clean) < 10:
        return False
    # Must be integer-valued (or float that rounds to int)
    if not np.allclose(clean, clean.astype(int), equal_nan=True):
        return False
    # Deduplicate to handle transaction-level IDs (same ID across line items)
    deduped = clean.drop_duplicates()
    if len(deduped) < 10:
        return False
    # After dedup, must be mostly monotonically increasing (>90%)
    diffs = deduped.diff().dropna()
    if len(diffs) == 0:
        return False
    pct_increasing = (diffs > 0).sum() / len(diffs)
    return pct_increasing > 0.9


def _infer_analysis_dtype(series: pd.Series) -> str:
    """Determine dtype for analysis purposes."""
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() < 10 and series.nunique() / max(len(series), 1) < 0.001:
            return "categorical"
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    try:
        pd.to_datetime(series.dropna().head(20), format="mixed")
        return "datetime"
    except (ValueError, TypeError):
        pass
    if series.nunique() / max(len(series), 1) > 0.5 and series.nunique() > 100:
        return "text"
    return "categorical"


def _safe_float(val) -> float:
    """Convert to float, return 0.0 on failure."""
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return 0.0
        return round(f, 4)
    except (TypeError, ValueError):
        return 0.0


def _compute_univariate_auc(feature_series: pd.Series, labels: pd.Series) -> float | None:
    """Compute univariate AUC of a feature against binary labels."""
    common = feature_series.dropna().index.intersection(labels.index)
    if len(common) < 20:
        return None
    try:
        from sklearn.metrics import roc_auc_score
        x = feature_series[common].values
        y = labels[common].values
        if len(np.unique(y)) < 2:
            return None
        auc = roc_auc_score(y, x)
        return round(float(auc), 4)
    except (ValueError, ImportError):
        return None


def _compute_trend(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str,
    numeric_col: pd.Series = None,
) -> pd.Series | None:
    """Compute 2nd half mean minus 1st half mean per customer."""
    dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
    valid = dates.notna()
    if valid.sum() < 10:
        return None

    mid = dates[valid].quantile(0.5)
    vals = numeric_col if numeric_col is not None else pd.to_numeric(df[col_name], errors="coerce")

    df_work = df[valid].assign(_val=vals[valid], _dt=dates[valid])

    first_half = df_work[df_work["_dt"] <= mid]
    second_half = df_work[df_work["_dt"] > mid]

    first_means = first_half.groupby(customer_id_col)["_val"].mean()
    second_means = second_half.groupby(customer_id_col)["_val"].mean()

    all_customers = first_means.index.union(second_means.index)
    first_means = first_means.reindex(all_customers, fill_value=0)
    second_means = second_means.reindex(all_customers, fill_value=0)

    return second_means - first_means


def _compute_categorical_shift(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str,
) -> pd.Series | None:
    """Compute Jaccard distance of value sets between 1st and 2nd half per customer."""
    dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
    valid = dates.notna()
    if valid.sum() < 10:
        return None

    mid = dates[valid].quantile(0.5)
    df_work = df[valid].assign(_dt=dates[valid])

    def jaccard_shift(group):
        group_dates = group["_dt"]
        first = set(group.loc[group_dates <= mid, col_name].dropna())
        second = set(group.loc[group_dates > mid, col_name].dropna())
        union = first | second
        if len(union) == 0:
            return 0.0
        return 1 - len(first & second) / len(union)

    try:
        return df_work.groupby(customer_id_col).apply(
            jaccard_shift, include_groups=False
        )
    except Exception:
        return None


def _compute_gap_profile(
    df_valid: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
) -> dict[str, pd.Series] | None:
    """Compute inter-event gap statistics per customer."""
    def gap_stats(group):
        sorted_dates = group["_dt"].sort_values()
        if len(sorted_dates) < 2:
            return pd.Series({
                "gap_avg": np.nan, "gap_std": np.nan,
                "gap_max": np.nan, "gap_cv": np.nan,
            })
        gaps = sorted_dates.diff().dt.days.dropna()
        if len(gaps) == 0:
            return pd.Series({
                "gap_avg": np.nan, "gap_std": np.nan,
                "gap_max": np.nan, "gap_cv": np.nan,
            })
        avg = gaps.mean()
        return pd.Series({
            "gap_avg": avg,
            "gap_std": gaps.std() if len(gaps) > 1 else 0,
            "gap_max": gaps.max(),
            "gap_cv": gaps.std() / avg if avg > 0 and len(gaps) > 1 else 0,
        })

    try:
        result = df_valid.groupby(customer_id_col).apply(
            gap_stats, include_groups=False
        )
        if isinstance(result, pd.DataFrame) and len(result) > 0:
            return {
                stat: result[stat]
                for stat in ["gap_avg", "gap_std", "gap_max", "gap_cv"]
                if stat in result.columns
            }
    except Exception as e:
        logger.warning("Gap profile computation failed: %s", e)

    return None
