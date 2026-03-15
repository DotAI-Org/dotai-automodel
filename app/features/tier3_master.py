"""Tier 3 master data features.

Computes static features from dealer/customer master data:
tenure, credit, territory, status.
"""
import numpy as np
import pandas as pd


def compute_master_features(
    df: pd.DataFrame, col_map: dict, customer_id_col: str
) -> pd.DataFrame:
    """Compute master data features.

    Master data is typically one row per customer.
    Expected roles: dealer_code, dealer_name, registration_date,
    status, credit_limit, territory.
    """
    features = pd.DataFrame(index=df[customer_id_col].unique())

    reg_date_col = _find_col(col_map, "registration_date")
    status_col = _find_col(col_map, "status")
    credit_col = _find_col(col_map, "credit_limit")
    territory_col = _find_col(col_map, "territory")

    # Deduplicate to one row per customer (take first)
    df_dedup = df.drop_duplicates(subset=[customer_id_col]).set_index(customer_id_col)

    # Registration tenure
    if reg_date_col:
        try:
            reg_dates = pd.to_datetime(df_dedup[reg_date_col])
            max_date = reg_dates.max()
            features["tenure_days"] = (max_date - reg_dates).dt.days
        except Exception:
            pass

    # Status (encode as binary: active=1, inactive=0)
    if status_col:
        try:
            active_keywords = {"active", "valid", "approved", "yes", "1"}
            features["status_active"] = df_dedup[status_col].str.lower().isin(
                active_keywords
            ).astype(int)
        except Exception:
            pass

    # Credit limit
    if credit_col:
        try:
            features["credit_limit"] = pd.to_numeric(
                df_dedup[credit_col], errors="coerce"
            )
        except Exception:
            pass

    # Territory (encode as category count for territory concentration)
    if territory_col:
        territory_counts = df[territory_col].value_counts()
        features["territory_size"] = df_dedup[territory_col].map(territory_counts)

    return features


def _find_col(col_map: dict, role: str) -> str | None:
    for col_name, col_role in col_map.items():
        if col_role == role:
            return col_name
    return None
