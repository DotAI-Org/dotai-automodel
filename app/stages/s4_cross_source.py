"""Cross-source feature computation.

Computes interaction features between primary and secondary data,
and between high-signal fields within the same dataset.
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_cross_source_features(
    primary_features: pd.DataFrame,
    secondary_features: pd.DataFrame,
    secondary_type: str,
) -> pd.DataFrame:
    """Compute interaction features between primary and secondary data.

    Join on index (customer_id). Left join: primary customers as base.
    """
    cross_features = pd.DataFrame(index=primary_features.index)

    # Left join secondary features
    combined = primary_features.join(secondary_features, how="left", rsuffix="_sec")

    if secondary_type == "loyalty":
        # Engagement-purchase ratio: points earned / monetary
        for pts_col in secondary_features.columns:
            if "points" in pts_col and "mean" in pts_col:
                for mon_col in primary_features.columns:
                    if "amount" in mon_col and "mean" in mon_col:
                        denom = combined[mon_col].replace(0, np.nan)
                        cross_features["engagement_purchase_ratio"] = (
                            combined[pts_col] / denom
                        )
                        break
                break

    elif secondary_type == "service":
        # Service-to-purchase ratio
        for svc_col in secondary_features.columns:
            if "ticket" in svc_col and "mean" in svc_col:
                for freq_col in primary_features.columns:
                    if "frequency" in freq_col and "90d" in freq_col:
                        denom = combined[freq_col].replace(0, np.nan)
                        cross_features["service_purchase_ratio"] = (
                            combined[svc_col] / denom
                        )
                        break
                break

    elif secondary_type == "field":
        # Visit-to-order conversion
        for visit_col in secondary_features.columns:
            if "visit" in visit_col and "frequency" in visit_col:
                for order_col in secondary_features.columns:
                    if "order_booked" in order_col and "mean" in order_col:
                        cross_features["visit_order_conversion"] = (
                            combined.get(order_col, 0)
                        )
                        break
                break

    return cross_features


def compute_interaction_features(
    feature_matrix: pd.DataFrame,
    signature: dict,
) -> pd.DataFrame:
    """For pairs of features with AUC > 0.60, compute ratio and product.

    Limits to top 5 high-signal features to avoid combinatorial explosion.
    """
    high_signal = []
    for field_name, field_sig in signature.items():
        auc = field_sig.get("univariate_churn_auc")
        if auc and auc > 0.60:
            # Find features derived from this field
            for col in feature_matrix.columns:
                if col.startswith(field_name) and "_mean" in col:
                    high_signal.append((col, auc))
                    break

    interactions = pd.DataFrame(index=feature_matrix.index)

    # Limit to top 5
    high_signal = sorted(high_signal, key=lambda x: x[1], reverse=True)[:5]

    for i, (feat_a, _) in enumerate(high_signal):
        for feat_b, _ in high_signal[i + 1:]:
            a = feature_matrix[feat_a].fillna(0)
            b = feature_matrix[feat_b].fillna(0)

            safe_b = b.replace(0, np.nan)
            ratio = a / safe_b
            # Only add if ratio has reasonable variance
            if ratio.std() > 0:
                interactions[f"{feat_a}_x_{feat_b}_ratio"] = ratio

    return interactions
