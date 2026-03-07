from typing import Any
import pandas as pd
import numpy as np
from fastapi import HTTPException

import logging

from app.session_store import store
from app.models.schemas import (
    MCQAnswers,
    FeaturesResponse,
    FeatureStat,
    LLMFeatureSelectionOutput,
    DSLFeature,
    LLMFeatureSuggestionOutput,
)
from app.llm.client import generate_structured

logger = logging.getLogger(__name__)


# --- Feature definitions for semantic leakage detection ---

FEATURE_DEFINITIONS = {
    # Tier 1
    "recency": "Days since the customer's last purchase date",
    "frequency_30d": "Number of transactions in the last 30 days",
    "frequency_60d": "Number of transactions in the last 60 days",
    "frequency_90d": "Number of transactions in the last 90 days",
    "monetary_total": "Total monetary value of all transactions",
    "monetary_avg": "Average monetary value per transaction",
    "frequency_trend": "Change in transaction count between first and second half of observation period",
    "monetary_trend": "Change in average transaction value between first and second half of observation period",
    "days_between_purchases_avg": "Average number of days between consecutive purchases",
    "days_between_purchases_std": "Standard deviation of days between consecutive purchases",
    # Tier 2
    "basket_diversity": "Number of distinct products or categories purchased",
    "category_concentration": "Proportion of purchases in the most frequent category",
    "channel_diversity": "Number of distinct sales channels used",
    "avg_basket_size": "Average quantity per transaction",
    "peak_vs_offpeak_ratio": "Ratio of holiday-season purchases to off-season purchases",
    "order_size_trend": "Change in average order size between first and second half of observation period",
    "product_mix_change": "Jaccard distance of product sets between first and second half of observation period",
    "region_loyalty": "Proportion of purchases in the most frequent region",
    "weekend_vs_weekday": "Ratio of weekend purchases to weekday purchases",
    "repeat_product_rate": "Proportion of products purchased more than once",
    "max_gap_between_purchases": "Longest gap in days between consecutive purchases",
    "purchase_regularity_score": "1 minus coefficient of variation of inter-purchase gaps (higher = more regular)",
}


# --- Tier 1: Universal features (always computed) ---

def compute_recency(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    return df.groupby(cust_col).apply(
        lambda g: (max_date - pd.to_datetime(g[date_col]).max()).days
    )


def compute_frequency_30d(df: pd.DataFrame, col_map: dict) -> pd.Series:
    return _frequency_window(df, col_map, 30)


def compute_frequency_60d(df: pd.DataFrame, col_map: dict) -> pd.Series:
    return _frequency_window(df, col_map, 60)


def compute_frequency_90d(df: pd.DataFrame, col_map: dict) -> pd.Series:
    return _frequency_window(df, col_map, 90)


def _frequency_window(df: pd.DataFrame, col_map: dict, days: int) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    cutoff = max_date - pd.Timedelta(days=days)
    recent = df[dates >= cutoff]
    counts = recent.groupby(cust_col).size()
    all_custs = df[cust_col].unique()
    return counts.reindex(all_custs, fill_value=0)


def compute_monetary_total(df: pd.DataFrame, col_map: dict) -> pd.Series:
    return df.groupby(col_map["customer_id"])[col_map["amount"]].sum()


def compute_monetary_avg(df: pd.DataFrame, col_map: dict) -> pd.Series:
    return df.groupby(col_map["customer_id"])[col_map["amount"]].mean()


def compute_frequency_trend(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    mid_date = max_date - (max_date - dates.min()) / 2

    first_half = df[dates < mid_date].groupby(cust_col).size()
    second_half = df[dates >= mid_date].groupby(cust_col).size()

    all_custs = df[cust_col].unique()
    first_half = first_half.reindex(all_custs, fill_value=0)
    second_half = second_half.reindex(all_custs, fill_value=0)

    # Positive = increasing frequency
    return second_half - first_half


def compute_monetary_trend(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    amount_col = col_map["amount"]
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    mid_date = max_date - (max_date - dates.min()) / 2

    first_half = df[dates < mid_date].groupby(cust_col)[amount_col].mean()
    second_half = df[dates >= mid_date].groupby(cust_col)[amount_col].mean()

    all_custs = df[cust_col].unique()
    first_half = first_half.reindex(all_custs, fill_value=0)
    second_half = second_half.reindex(all_custs, fill_value=0)

    return second_half - first_half


def compute_days_between_purchases_avg(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    def _avg_gap(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 2:
            return np.nan
        diffs = dates.diff().dt.days.dropna()
        return diffs.mean()

    return df.groupby(cust_col).apply(_avg_gap)


def compute_days_between_purchases_std(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    def _std_gap(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 3:
            return np.nan
        diffs = dates.diff().dt.days.dropna()
        return diffs.std()

    return df.groupby(cust_col).apply(_std_gap)


# --- Tier 2: Industry-specific features ---

def compute_basket_diversity(df: pd.DataFrame, col_map: dict) -> pd.Series:
    product_col = col_map.get("product") or col_map.get("category")
    cust_col = col_map["customer_id"]
    return df.groupby(cust_col)[product_col].nunique()


def compute_category_concentration(df: pd.DataFrame, col_map: dict) -> pd.Series:
    cat_col = col_map["category"]
    cust_col = col_map["customer_id"]

    def _concentration(g):
        counts = g[cat_col].value_counts(normalize=True)
        return counts.iloc[0] if len(counts) > 0 else 1.0

    return df.groupby(cust_col).apply(_concentration)


def compute_channel_diversity(df: pd.DataFrame, col_map: dict) -> pd.Series:
    channel_col = col_map["channel"]
    cust_col = col_map["customer_id"]
    return df.groupby(cust_col)[channel_col].nunique()


def compute_avg_basket_size(df: pd.DataFrame, col_map: dict) -> pd.Series:
    qty_col = col_map["quantity"]
    cust_col = col_map["customer_id"]
    return df.groupby(cust_col)[qty_col].mean()


def compute_peak_vs_offpeak_ratio(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    dates = pd.to_datetime(df[date_col])

    df_copy = df.copy()
    df_copy["_month"] = dates.dt.month
    # Peak months: Nov, Dec, Jan (holiday season)
    df_copy["_is_peak"] = df_copy["_month"].isin([11, 12, 1])

    def _ratio(g):
        peak = g["_is_peak"].sum()
        off = (~g["_is_peak"]).sum()
        return peak / max(off, 1)

    return df_copy.groupby(cust_col).apply(_ratio)


def compute_order_size_trend(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    amount_col = col_map.get("amount") or col_map.get("quantity")
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    mid_date = max_date - (max_date - dates.min()) / 2

    first_half = df[dates < mid_date].groupby(cust_col)[amount_col].mean()
    second_half = df[dates >= mid_date].groupby(cust_col)[amount_col].mean()

    all_custs = df[cust_col].unique()
    first_half = first_half.reindex(all_custs, fill_value=0)
    second_half = second_half.reindex(all_custs, fill_value=0)

    return second_half - first_half


def compute_product_mix_change(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]
    product_col = col_map.get("product") or col_map.get("category")
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()
    mid_date = max_date - (max_date - dates.min()) / 2

    def _mix_change(g):
        g_dates = pd.to_datetime(g[date_col])
        first = set(g[g_dates < mid_date][product_col].unique())
        second = set(g[g_dates >= mid_date][product_col].unique())
        if not first and not second:
            return 0.0
        union = first | second
        if not union:
            return 0.0
        intersection = first & second
        return 1.0 - len(intersection) / len(union)

    return df.groupby(cust_col).apply(_mix_change)


def compute_region_loyalty(df: pd.DataFrame, col_map: dict) -> pd.Series:
    region_col = col_map["region"]
    cust_col = col_map["customer_id"]

    def _loyalty(g):
        counts = g[region_col].value_counts(normalize=True)
        return counts.iloc[0] if len(counts) > 0 else 1.0

    return df.groupby(cust_col).apply(_loyalty)


def compute_weekend_vs_weekday(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    df_copy = df.copy()
    df_copy["_dow"] = pd.to_datetime(df_copy[date_col]).dt.dayofweek
    df_copy["_is_weekend"] = df_copy["_dow"] >= 5

    def _ratio(g):
        wkend = g["_is_weekend"].sum()
        wkday = (~g["_is_weekend"]).sum()
        return wkend / max(wkday, 1)

    return df_copy.groupby(cust_col).apply(_ratio)


def compute_repeat_product_rate(df: pd.DataFrame, col_map: dict) -> pd.Series:
    product_col = col_map.get("product")
    cust_col = col_map["customer_id"]

    def _repeat_rate(g):
        counts = g[product_col].value_counts()
        if len(counts) == 0:
            return 0.0
        return (counts > 1).sum() / len(counts)

    return df.groupby(cust_col).apply(_repeat_rate)


def compute_max_gap_between_purchases(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    def _max_gap(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 2:
            return np.nan
        diffs = dates.diff().dt.days.dropna()
        return diffs.max()

    return df.groupby(cust_col).apply(_max_gap)


def compute_purchase_regularity_score(df: pd.DataFrame, col_map: dict) -> pd.Series:
    date_col = col_map["transaction_date"]
    cust_col = col_map["customer_id"]

    def _regularity(g):
        dates = pd.to_datetime(g[date_col]).sort_values()
        if len(dates) < 3:
            return np.nan
        diffs = dates.diff().dt.days.dropna()
        mean = diffs.mean()
        if mean == 0:
            return 1.0
        cv = diffs.std() / mean  # coefficient of variation
        return max(0, 1.0 - cv)  # higher = more regular

    return df.groupby(cust_col).apply(_regularity)


# --- Feature catalog registry ---

TIER1_FEATURES = {
    "recency": compute_recency,
    "frequency_30d": compute_frequency_30d,
    "frequency_60d": compute_frequency_60d,
    "frequency_90d": compute_frequency_90d,
    "monetary_total": compute_monetary_total,
    "monetary_avg": compute_monetary_avg,
    "frequency_trend": compute_frequency_trend,
    "monetary_trend": compute_monetary_trend,
    "days_between_purchases_avg": compute_days_between_purchases_avg,
    "days_between_purchases_std": compute_days_between_purchases_std,
}

# Each entry: (function, list of required column roles)
TIER2_FEATURES = {
    "basket_diversity": (compute_basket_diversity, ["product"]),
    "category_concentration": (compute_category_concentration, ["category"]),
    "channel_diversity": (compute_channel_diversity, ["channel"]),
    "avg_basket_size": (compute_avg_basket_size, ["quantity"]),
    "peak_vs_offpeak_ratio": (compute_peak_vs_offpeak_ratio, ["transaction_date"]),
    "order_size_trend": (compute_order_size_trend, ["amount"]),
    "product_mix_change": (compute_product_mix_change, ["product"]),
    "region_loyalty": (compute_region_loyalty, ["region"]),
    "weekend_vs_weekday": (compute_weekend_vs_weekday, ["transaction_date"]),
    "repeat_product_rate": (compute_repeat_product_rate, ["product"]),
    "max_gap_between_purchases": (compute_max_gap_between_purchases, ["transaction_date"]),
    "purchase_regularity_score": (compute_purchase_regularity_score, ["transaction_date"]),
}

# Tier 1 requires these roles to exist
TIER1_REQUIRED_ROLES = ["customer_id", "transaction_date", "amount"]


async def handle(
    session_id: str, session: dict[str, Any], body: MCQAnswers
) -> FeaturesResponse:
    column_mapping = session.get("column_mapping")
    hypothesis = session.get("hypothesis")
    df = session.get("dataframe")

    if column_mapping is None or hypothesis is None or df is None:
        raise HTTPException(
            status_code=400,
            detail="Hypothesis stage must be completed first.",
        )

    # Build role -> column name mapping
    col_map = _build_col_map(column_mapping)

    # Validate required roles exist
    for role in TIER1_REQUIRED_ROLES:
        if role not in col_map:
            raise HTTPException(
                status_code=400,
                detail=f"Required column role '{role}' not found in mapping.",
            )

    # --- Time split: compute features from observation window only ---
    from app.stages.s5_labels import _get_churn_window

    date_col = col_map["transaction_date"]
    dates = pd.to_datetime(df[date_col])
    max_date = dates.max()

    churn_window_days = _get_churn_window(df, col_map, body.answers)
    cutoff_date = max_date - pd.Timedelta(days=churn_window_days)

    df_obs = df[dates <= cutoff_date].copy()

    if len(df_obs) == 0:
        raise HTTPException(
            status_code=400,
            detail="Not enough data before cutoff date. Try a shorter churn window.",
        )

    # Compute Tier 1 features from observation window only
    feature_matrix = pd.DataFrame()
    tier1_names = []
    for name, func in TIER1_FEATURES.items():
        try:
            if name in ("monetary_total", "monetary_avg", "monetary_trend") and "amount" not in col_map:
                continue
            feature_matrix[name] = func(df_obs, col_map)
            tier1_names.append(name)
        except Exception:
            continue

    # Determine available Tier 2 features based on columns
    available_tier2 = _get_available_tier2(col_map)

    # Ask LLM to select Tier 2 features
    tier2_names = []
    if available_tier2:
        selected = await _select_tier2_features(
            available_tier2, column_mapping, hypothesis, body.answers
        )
        for name in selected:
            if name in TIER2_FEATURES:
                func, _ = TIER2_FEATURES[name]
                try:
                    feature_matrix[name] = func(df_obs, col_map)
                    tier2_names.append(name)
                except Exception:
                    continue

    # User-derived DSL features from free text
    user_dsl_names = []
    user_dsl_features = []
    free_text = session.get("free_text")
    if free_text:
        try:
            from app.agent.feature_dsl import execute_dsl_features
            extracted = await _extract_user_features(
                free_text, col_map, tier1_names + tier2_names
            )
            if extracted:
                user_dsl_features = extracted
                dsl_df = execute_dsl_features(df_obs, col_map, extracted)
                for col_name in dsl_df.columns:
                    feature_matrix[col_name] = dsl_df[col_name]
                    user_dsl_names.append(col_name)
        except Exception as e:
            logger.warning(f"User feature extraction failed: {e}")

    # Build stats
    stats = []
    for col in feature_matrix.columns:
        s = feature_matrix[col]
        stats.append(FeatureStat(
            name=col,
            mean=round(float(s.mean()), 4) if not s.isna().all() else None,
            median=round(float(s.median()), 4) if not s.isna().all() else None,
            null_pct=round(float(s.isna().mean() * 100), 2),
        ))

    feature_tiers = {"tier1": tier1_names, "tier2": tier2_names}
    if user_dsl_names:
        feature_tiers["user"] = user_dsl_names

    store.update(session_id, {
        "stage": 4,
        "mcq_answers": body.answers,
        "feature_matrix": feature_matrix,
        "col_map": col_map,
        "tier1_features": tier1_names,
        "tier2_features": tier2_names,
        "user_dsl_features": [f.model_dump() for f in user_dsl_features],
        "churn_window_days": churn_window_days,
    })

    return FeaturesResponse(
        feature_count=len(feature_matrix.columns),
        user_count=len(feature_matrix),
        feature_tiers=feature_tiers,
        stats=stats,
    )


async def _extract_user_features(
    free_text: str, col_map: dict, existing_features: list[str]
) -> list[DSLFeature]:
    """Translate user free text into DSL feature definitions via LLM."""
    available_cols = "\n".join(f"- {role}: {col}" for role, col in col_map.items())
    existing_text = ", ".join(existing_features) if existing_features else "None"

    dsl_ops_doc = """Available DSL operations:
- aggregate: {column, function (sum/mean/std/min/max/count)}
- aggregate_window: {column, function, window_days}
- ratio: {numerator_column, denominator_column, function}
- trend: {column, function (sum/mean/count)}
- conditional_count: {column, condition (gt/lt/eq/ne), value}
- nunique: {column}
- gap_stat: {stat (mean/std/max/min)}"""

    prompt = f"""You are a feature engineer. A user described signals they think matter for churn prediction.

USER INPUT:
{free_text}

AVAILABLE COLUMNS (role: column_name):
{available_cols}

EXISTING FEATURES (already computed):
{existing_text}

{dsl_ops_doc}

Translate the user's described signals into DSL feature definitions.
Only create features that can be computed from the available columns.
Do not duplicate existing features.

For each feature, provide:
- name: snake_case feature name
- description: what this feature measures
- operation: one of the DSL operations above
- params_json: JSON string of the operation parameters

Return JSON with:
- "suggested_features": array of feature objects
- "reasoning": explanation"""

    result = await generate_structured(prompt, LLMFeatureSuggestionOutput)
    return result.suggested_features


def _build_col_map(column_mapping: dict) -> dict[str, str]:
    """Map role -> column name from the column mapping."""
    col_map = {}
    for col in column_mapping["columns"]:
        role = col["llm_role"]
        if role != "other":
            col_map[role] = col["name"]
    return col_map


def _get_available_tier2(col_map: dict) -> list[str]:
    """Return Tier 2 feature names whose required columns exist."""
    available = []
    for name, (_, required_roles) in TIER2_FEATURES.items():
        if all(role in col_map for role in required_roles):
            available.append(name)
    return available


def compute_feature_matrix(
    df_obs: pd.DataFrame,
    col_map: dict,
    column_mapping: dict,
    hypothesis: dict,
    mcq_answers: dict,
    excluded_features: list[str] | None = None,
    dsl_features: list | None = None,
) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    """Compute features from observation window data.

    Returns (feature_matrix, tier1_names, tier2_names, dsl_names).
    This function is used by both the stage handler and the agent loop.
    """
    from app.agent.feature_dsl import execute_dsl_features

    excluded_features = excluded_features or []
    dsl_features = dsl_features or []

    feature_matrix = pd.DataFrame()

    # Tier 1
    tier1_names = []
    for name, func in TIER1_FEATURES.items():
        if name in excluded_features:
            continue
        try:
            if name in ("monetary_total", "monetary_avg", "monetary_trend") and "amount" not in col_map:
                continue
            feature_matrix[name] = func(df_obs, col_map)
            tier1_names.append(name)
        except Exception:
            continue

    # Tier 2
    available_tier2 = _get_available_tier2(col_map)
    tier2_names = []
    if available_tier2:
        # Filter out excluded
        available_tier2 = [f for f in available_tier2 if f not in excluded_features]
        if available_tier2:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # We're already in an async context; cannot call await from sync.
                # Use tier2 selection synchronously by running in a new event loop in a thread.
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    selected = loop.run_in_executor(
                        pool,
                        lambda: asyncio.run(_select_tier2_features(
                            available_tier2, column_mapping, hypothesis, mcq_answers
                        ))
                    )
                    # This won't work in sync context. Fall back to using all available.
                    selected = available_tier2
            else:
                selected = asyncio.run(_select_tier2_features(
                    available_tier2, column_mapping, hypothesis, mcq_answers
                ))

            for name in selected:
                if name in TIER2_FEATURES and name not in excluded_features:
                    func, _ = TIER2_FEATURES[name]
                    try:
                        feature_matrix[name] = func(df_obs, col_map)
                        tier2_names.append(name)
                    except Exception:
                        continue

    # DSL features
    dsl_names = []
    if dsl_features:
        dsl_df = execute_dsl_features(df_obs, col_map, dsl_features, excluded=excluded_features)
        for col in dsl_df.columns:
            feature_matrix[col] = dsl_df[col]
            dsl_names.append(col)

    return feature_matrix, tier1_names, tier2_names, dsl_names


async def compute_feature_matrix_async(
    df_obs: pd.DataFrame,
    col_map: dict,
    column_mapping: dict,
    hypothesis: dict,
    mcq_answers: dict,
    excluded_features: list[str] | None = None,
    dsl_features: list | None = None,
) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    """Async version of compute_feature_matrix. Used by agent loop."""
    from app.agent.feature_dsl import execute_dsl_features

    excluded_features = excluded_features or []
    dsl_features = dsl_features or []

    feature_matrix = pd.DataFrame()

    # Tier 1
    tier1_names = []
    for name, func in TIER1_FEATURES.items():
        if name in excluded_features:
            continue
        try:
            if name in ("monetary_total", "monetary_avg", "monetary_trend") and "amount" not in col_map:
                continue
            feature_matrix[name] = func(df_obs, col_map)
            tier1_names.append(name)
        except Exception:
            continue

    # Tier 2
    available_tier2 = _get_available_tier2(col_map)
    tier2_names = []
    if available_tier2:
        available_tier2 = [f for f in available_tier2 if f not in excluded_features]
        if available_tier2:
            selected = await _select_tier2_features(
                available_tier2, column_mapping, hypothesis, mcq_answers
            )
            for name in selected:
                if name in TIER2_FEATURES and name not in excluded_features:
                    func, _ = TIER2_FEATURES[name]
                    try:
                        feature_matrix[name] = func(df_obs, col_map)
                        tier2_names.append(name)
                    except Exception:
                        continue

    # DSL features
    dsl_names = []
    if dsl_features:
        dsl_df = execute_dsl_features(df_obs, col_map, dsl_features, excluded=excluded_features)
        for col in dsl_df.columns:
            feature_matrix[col] = dsl_df[col]
            dsl_names.append(col)

    return feature_matrix, tier1_names, tier2_names, dsl_names


async def _select_tier2_features(
    available: list[str],
    column_mapping: dict,
    hypothesis: dict,
    mcq_answers: dict,
) -> list[str]:
    feature_list = "\n".join(f"- {name}" for name in available)
    col_info = "\n".join(
        f"- {c['name']}: {c['llm_role']}" for c in column_mapping["columns"]
    )
    answers_text = "\n".join(f"- {k}: {v}" for k, v in mcq_answers.items())

    prompt = f"""You are a data scientist. Select which features to compute for a churn prediction model.

Business hypothesis: {hypothesis['hypothesis']['type']} (confidence: {hypothesis['hypothesis']['confidence']})
Reasoning: {hypothesis['hypothesis']['reasoning']}

Available columns:
{col_info}

User's answers to business questions:
{answers_text}

Available Tier 2 features (these are pre-built functions, you just need to pick which ones to use):
{feature_list}

Select all features that are relevant for this business type and available data.
Return a JSON object with:
- "selected_features": array of feature names from the list above
- "reasoning": brief explanation of your selections"""

    result = await generate_structured(prompt, LLMFeatureSelectionOutput)
    # Filter to only features that are actually available
    return [f for f in result.selected_features if f in available]
