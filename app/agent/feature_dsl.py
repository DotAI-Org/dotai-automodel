import logging
import pandas as pd
import numpy as np

from app.models.schemas import DSLFeature

logger = logging.getLogger(__name__)


def execute_dsl_feature(
    df: pd.DataFrame,
    col_map: dict,
    feature_def: DSLFeature,
) -> pd.Series:
    """Execute a single DSL feature definition and return a Series indexed by customer_id."""
    cust_col = col_map["customer_id"]
    op = feature_def.operation
    params = feature_def.params

    handlers = {
        "aggregate": _op_aggregate,
        "aggregate_window": _op_aggregate_window,
        "ratio": _op_ratio,
        "trend": _op_trend,
        "conditional_count": _op_conditional_count,
        "nunique": _op_nunique,
        "gap_stat": _op_gap_stat,
    }

    handler = handlers.get(op)
    if handler is None:
        raise ValueError(f"Unknown DSL operation: {op}")

    return handler(df, col_map, cust_col, params)


def execute_dsl_features(
    df: pd.DataFrame,
    col_map: dict,
    feature_defs: list[DSLFeature],
    excluded: list[str] | None = None,
) -> pd.DataFrame:
    """Execute multiple DSL feature definitions. Returns DataFrame indexed by customer_id."""
    excluded = excluded or []
    result = pd.DataFrame(index=df[col_map["customer_id"]].unique())
    result.index.name = col_map["customer_id"]

    for feat_def in feature_defs:
        if feat_def.name in excluded:
            continue
        try:
            series = execute_dsl_feature(df, col_map, feat_def)
            result[feat_def.name] = series
        except Exception as e:
            logger.warning(f"DSL feature '{feat_def.name}' failed: {e}")
            continue

    return result


def _resolve_column(col_map: dict, col_ref: str) -> str:
    """Resolve a column reference. If it matches a role in col_map, return the mapped name. Otherwise return as-is."""
    return col_map.get(col_ref, col_ref)


def _op_aggregate(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    column = _resolve_column(col_map, params["column"])
    func = params["func"]
    grouped = df.groupby(cust_col)[column]
    return _apply_agg_func(grouped, func)


def _op_aggregate_window(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    column = _resolve_column(col_map, params["column"])
    func = params["func"]
    window_days = params["window_days"]
    date_col = col_map["transaction_date"]

    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    cutoff = max_date - pd.Timedelta(days=window_days)
    recent = df[dates >= cutoff]

    all_custs = df[cust_col].unique()
    if len(recent) == 0:
        return pd.Series(0, index=all_custs)

    grouped = recent.groupby(cust_col)[column]
    result = _apply_agg_func(grouped, func)
    return result.reindex(all_custs, fill_value=0)


def _op_ratio(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    num_params = params["numerator"]
    den_params = params["denominator"]

    # Compute numerator
    num_col = _resolve_column(col_map, num_params["column"])
    num_func = num_params["func"]
    if "window_days" in num_params:
        date_col = col_map["transaction_date"]
        dates = pd.to_datetime(df[date_col])
        max_date = dates.max()
        cutoff = max_date - pd.Timedelta(days=num_params["window_days"])
        num_df = df[dates >= cutoff]
    else:
        num_df = df

    all_custs = df[cust_col].unique()

    if len(num_df) > 0:
        numerator = _apply_agg_func(num_df.groupby(cust_col)[num_col], num_func)
    else:
        numerator = pd.Series(0, index=all_custs)
    numerator = numerator.reindex(all_custs, fill_value=0)

    # Compute denominator
    den_col = _resolve_column(col_map, den_params["column"])
    den_func = den_params["func"]
    if "window_days" in den_params:
        date_col = col_map["transaction_date"]
        dates = pd.to_datetime(df[date_col])
        max_date = dates.max()
        cutoff = max_date - pd.Timedelta(days=den_params["window_days"])
        den_df = df[dates >= cutoff]
    else:
        den_df = df

    if len(den_df) > 0:
        denominator = _apply_agg_func(den_df.groupby(cust_col)[den_col], den_func)
    else:
        denominator = pd.Series(0, index=all_custs)
    denominator = denominator.reindex(all_custs, fill_value=0)

    # Avoid division by zero
    return numerator / denominator.replace(0, np.nan)


def _op_trend(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    column = _resolve_column(col_map, params["column"])
    func = params["func"]
    date_col = col_map["transaction_date"]

    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    min_date = dates.min()
    mid_date = min_date + (max_date - min_date) / 2

    all_custs = df[cust_col].unique()

    first_half = df[dates < mid_date]
    second_half = df[dates >= mid_date]

    if len(first_half) > 0:
        first_vals = _apply_agg_func(first_half.groupby(cust_col)[column], func)
    else:
        first_vals = pd.Series(0, index=all_custs)
    first_vals = first_vals.reindex(all_custs, fill_value=0)

    if len(second_half) > 0:
        second_vals = _apply_agg_func(second_half.groupby(cust_col)[column], func)
    else:
        second_vals = pd.Series(0, index=all_custs)
    second_vals = second_vals.reindex(all_custs, fill_value=0)

    return second_vals - first_vals


def _op_conditional_count(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    column = _resolve_column(col_map, params["column"])
    condition = params["condition"]  # e.g. "> 50", "== 'online'"

    # Parse condition
    op_str = condition.strip()
    if op_str.startswith(">="):
        threshold = float(op_str[2:].strip())
        mask = df[column] >= threshold
    elif op_str.startswith("<="):
        threshold = float(op_str[2:].strip())
        mask = df[column] <= threshold
    elif op_str.startswith(">"):
        threshold = float(op_str[1:].strip())
        mask = df[column] > threshold
    elif op_str.startswith("<"):
        threshold = float(op_str[1:].strip())
        mask = df[column] < threshold
    elif op_str.startswith("=="):
        val = op_str[2:].strip().strip("'\"")
        try:
            val = float(val)
        except ValueError:
            pass
        mask = df[column] == val
    elif op_str.startswith("!="):
        val = op_str[2:].strip().strip("'\"")
        try:
            val = float(val)
        except ValueError:
            pass
        mask = df[column] != val
    else:
        raise ValueError(f"Cannot parse condition: {condition}")

    filtered = df[mask]
    all_custs = df[cust_col].unique()
    counts = filtered.groupby(cust_col).size()
    return counts.reindex(all_custs, fill_value=0)


def _op_nunique(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    column = _resolve_column(col_map, params["column"])
    return df.groupby(cust_col)[column].nunique()


def _op_gap_stat(df: pd.DataFrame, col_map: dict, cust_col: str, params: dict) -> pd.Series:
    func = params["func"]  # "max", "min", "mean", "std", "median"
    date_col = col_map["transaction_date"]

    def _compute_gap(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 2:
            return np.nan
        diffs = dates.diff().dt.days.dropna()
        if func == "max":
            return diffs.max()
        elif func == "min":
            return diffs.min()
        elif func == "mean":
            return diffs.mean()
        elif func == "std":
            return diffs.std()
        elif func == "median":
            return diffs.median()
        else:
            raise ValueError(f"Unknown gap_stat func: {func}")

    return df.groupby(cust_col).apply(_compute_gap, include_groups=False)


def _apply_agg_func(grouped, func: str) -> pd.Series:
    if func == "sum":
        return grouped.sum()
    elif func == "mean":
        return grouped.mean()
    elif func == "count":
        return grouped.count()
    elif func == "max":
        return grouped.max()
    elif func == "min":
        return grouped.min()
    elif func == "std":
        return grouped.std()
    elif func == "median":
        return grouped.median()
    elif func == "nunique":
        return grouped.nunique()
    else:
        raise ValueError(f"Unknown aggregation function: {func}")
