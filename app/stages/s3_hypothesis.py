"""Stage 3: Exhaustive field analysis, auto churn window, grounded hypothesis.

Revised flow:
  3a. Exhaustive field analysis (4 analyses per dtype on every field)
  3b. Auto-select churn window (test 6 candidates)
  3c. LLM hypothesis grounded in computed facts
  3d. Generate findings for user confirmation
  3e. MCQs with defaults (shown only on "Let me correct")
"""
import logging
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException

from app.session_store import store
from app.models.schemas import (
    BusinessHypothesis,
    MCQuestion,
    MCQOption,
    HypothesisResponse,
    LLMHypothesisOutput,
)
from app.llm.client import generate_structured, get_reasoning_model
from app.stages.s3_field_analysis import analyze_all_fields
from app.stages.s3_churn_window import auto_select_churn_window, generate_labels

logger = logging.getLogger(__name__)


async def handle(
    session_id: str,
    session: dict[str, Any],
    free_text: str | None = None,
) -> HypothesisResponse:
    """Run exhaustive field analysis, auto churn window, grounded hypothesis."""
    column_mapping = session.get("column_mapping")
    profile = session.get("profile")
    if not column_mapping or not profile:
        raise HTTPException(
            status_code=400,
            detail="Column mapping required. Run column-mapping first.",
        )

    df = session.get("dataframe")
    if df is None:
        raise HTTPException(status_code=400, detail="No dataframe in session.")

    # Build col_map: {column_name: role}
    col_map = {}
    for c in column_mapping["columns"]:
        col_map[c["name"]] = c["llm_role"]

    customer_id_col = _get_col(col_map, "customer_id")
    date_col = _get_col(col_map, "transaction_date")

    if not customer_id_col:
        raise HTTPException(status_code=400, detail="No customer_id column mapped.")

    # --- 3a. Exhaustive field analysis ---
    logger.info("Running exhaustive field analysis on %d columns", len(col_map))

    # Generate preliminary labels with 90-day default for univariate analysis
    preliminary_labels = None
    if date_col:
        preliminary_labels = generate_labels(df, customer_id_col, date_col, window=90)

    signature, feature_matrix = analyze_all_fields(
        df, col_map, customer_id_col, date_col, labels=preliminary_labels,
    )
    logger.info(
        "Field analysis complete: %d fields, %d features, %d customers",
        len(signature), len(feature_matrix.columns), len(feature_matrix),
    )

    # --- 3b. Auto churn window ---
    churn_window_result = None
    if date_col and len(feature_matrix) > 0:
        logger.info("Testing 6 churn window candidates")
        churn_window_result = auto_select_churn_window(
            df, feature_matrix, customer_id_col, date_col,
        )
        selected_window = churn_window_result["selected_window"]

        # Recompute labels with selected window
        final_labels = generate_labels(df, customer_id_col, date_col, window=selected_window)

        # Recompute univariate AUCs with correct labels
        signature = _recompute_univariate_aucs(signature, feature_matrix, final_labels)

        # Add adaptive gap as a feature
        if churn_window_result.get("adaptive_gap") is not None:
            feature_matrix["gap_vs_personal_median"] = churn_window_result["adaptive_gap"]

        logger.info("Selected churn window: %d days", selected_window)
    else:
        selected_window = 90
        final_labels = preliminary_labels

    # --- 3c. LLM hypothesis grounded in computed facts ---
    prompt = _build_grounded_prompt(signature, churn_window_result, profile, free_text)
    reasoning_model = get_reasoning_model()
    llm_output = await generate_structured(prompt, LLMHypothesisOutput, model=reasoning_model)

    hypothesis = BusinessHypothesis(
        type=llm_output.business_type,
        confidence=llm_output.confidence,
        reasoning=llm_output.reasoning,
    )

    # --- 3d. Generate findings ---
    findings = _generate_findings(signature, churn_window_result)

    # --- 3e. MCQs with defaults ---
    questions = []
    for q in llm_output.questions:
        questions.append(MCQuestion(
            id=q.id,
            question=q.question,
            options=[MCQOption(label=o.label, value=o.value) for o in q.options],
            context=q.context,
        ))

    # Store everything in session
    update_data = {
        "stage": 3,
        "hypothesis": {"hypothesis": hypothesis.model_dump(), "questions": [q.model_dump() for q in questions]},
        "field_analysis_signature": signature,
        "feature_matrix": feature_matrix,
        "labels": final_labels,
        "churn_window_days": selected_window,
        "churn_window_results": churn_window_result["all_results"] if churn_window_result else [],
        "findings": findings,
        "col_map": col_map,
    }
    if free_text:
        update_data["free_text"] = free_text
    store.update(session_id, update_data)

    # Build serializable churn_window for response (strip non-JSON-safe fields)
    if churn_window_result:
        churn_window_response = {
            "selected_window": churn_window_result["selected_window"],
            "all_results": churn_window_result.get("all_results", []),
        }
    else:
        churn_window_response = {"selected_window": selected_window, "all_results": []}

    return HypothesisResponse(
        hypothesis=hypothesis,
        questions=questions,
        findings=findings,
        churn_window=churn_window_response,
    )


def _get_col(col_map: dict, role: str) -> str | None:
    """Find the column name assigned to a given role."""
    for col_name, col_role in col_map.items():
        if col_role == role:
            return col_name
    return None


def _recompute_univariate_aucs(
    signature: dict,
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
) -> dict:
    """Recompute univariate AUCs with the auto-selected churn window labels."""
    from app.stages.s3_field_analysis import _compute_univariate_auc

    for field_name, field_sig in signature.items():
        if field_sig.get("dtype") in ("numeric", "categorical"):
            # Find the mean feature for this field
            mean_col = f"{field_name}_mean"
            if mean_col in feature_matrix.columns:
                auc = _compute_univariate_auc(feature_matrix[mean_col], labels)
                if auc is not None:
                    field_sig["univariate_churn_auc"] = auc

            # Also check diversity feature for categorical
            div_col = f"{field_name}_diversity"
            if div_col in feature_matrix.columns:
                auc = _compute_univariate_auc(feature_matrix[div_col], labels)
                if auc is not None:
                    field_sig["diversity_churn_auc"] = auc

    return signature


def _generate_findings(signature: dict, churn_window_result: dict | None) -> dict:
    """Build the findings object shown to the user."""
    findings = {
        "purchase_pattern": {},
        "churn_threshold": {},
        "seasonality": {},
        "revenue_concentration": {},
        "signals": [],
        "cross_file": {},
    }

    # Collect signals with AUC > 0.55
    signals = []
    for field_name, field_sig in signature.items():
        auc = field_sig.get("univariate_churn_auc")
        if auc and auc > 0.55 and field_sig.get("role") != "customer_id":
            signals.append({
                "field": field_name,
                "role": field_sig.get("role", "other"),
                "auc": auc,
                "dtype": field_sig.get("dtype", "unknown"),
                "stats": {
                    k: v for k, v in field_sig.items()
                    if k not in ("dtype", "role", "univariate_churn_auc", "diversity_churn_auc")
                },
            })

    findings["signals"] = sorted(signals, key=lambda s: s["auc"], reverse=True)[:5]

    # Churn threshold
    if churn_window_result:
        findings["churn_threshold"] = {
            "selected_window": churn_window_result["selected_window"],
            "all_results": churn_window_result["all_results"],
        }

    # Seasonality
    for field_name, field_sig in signature.items():
        if field_sig.get("dtype") == "datetime" and field_sig.get("is_seasonal"):
            findings["seasonality"] = {
                "field": field_name,
                "seasonal_index": field_sig.get("seasonal_index", {}),
            }
            break

    # Purchase pattern from gap stats
    for field_name, field_sig in signature.items():
        if field_sig.get("role") == "transaction_date" and field_sig.get("gap_median"):
            findings["purchase_pattern"] = {
                "median_gap_days": field_sig["gap_median"],
                "recency_median": field_sig.get("recency_median", 0),
                "frequency_30d_median": field_sig.get("frequency_30d_median", 0),
            }
            break

    return findings


def _build_grounded_prompt(
    signature: dict,
    churn_window_result: dict | None,
    profile: dict,
    free_text: str | None = None,
) -> str:
    """Build LLM prompt grounded in computed facts from field analysis."""
    # Format signature into readable sections
    numeric_section = []
    categorical_section = []
    datetime_section = []

    for field_name, field_sig in signature.items():
        dtype = field_sig.get("dtype", "text")
        role = field_sig.get("role", "other")

        if dtype == "numeric":
            line = (
                f"- {field_name} (role={role}): "
                f"mean={field_sig.get('mean', 'N/A')}, "
                f"median={field_sig.get('median', 'N/A')}, "
                f"skew={field_sig.get('skew', 'N/A')}"
            )
            auc = field_sig.get("univariate_churn_auc")
            if auc:
                line += f". Univariate churn AUC={auc}"
            trend = field_sig.get("trend_direction")
            if trend:
                line += f". Trend: {trend}"
            numeric_section.append(line)

        elif dtype == "categorical":
            top5 = field_sig.get("top_5", {})
            top5_str = ", ".join(f"{k} ({v}%)" for k, v in list(top5.items())[:3])
            line = (
                f"- {field_name} (role={role}): "
                f"top values: {top5_str}. "
                f"Diversity per customer: {field_sig.get('avg_diversity_per_customer', 'N/A')}"
            )
            churn_rates = field_sig.get("churn_rate_by_value", {})
            if churn_rates:
                top_churn = sorted(churn_rates.items(), key=lambda x: x[1], reverse=True)[:2]
                churn_str = ", ".join(f"{k}={v}" for k, v in top_churn)
                line += f". Churn rates: {churn_str}"
            categorical_section.append(line)

        elif dtype == "datetime":
            line = (
                f"- {field_name} (role={role}): "
                f"range {field_sig.get('min', 'N/A')} to {field_sig.get('max', 'N/A')}. "
                f"Median purchase gap: {field_sig.get('gap_median', 'N/A')} days"
            )
            if field_sig.get("is_seasonal"):
                idx = field_sig.get("seasonal_index", {})
                peaks = {k: v for k, v in idx.items() if v > 1.2}
                if peaks:
                    line += f". Seasonal peaks: {peaks}"
            datetime_section.append(line)

    prompt = f"""You are a business analyst. Here is the complete field analysis of a dataset:

NUMERIC FIELDS:
{chr(10).join(numeric_section) if numeric_section else "None"}

CATEGORICAL FIELDS:
{chr(10).join(categorical_section) if categorical_section else "None"}

DATETIME FIELDS:
{chr(10).join(datetime_section) if datetime_section else "None"}
"""

    if churn_window_result:
        tested = [r for r in churn_window_result["all_results"] if r.get("f1") is not None]
        if tested:
            window_lines = [
                f"- {r['window']} days: F1={r['f1']}, churn rate={r['churn_rate']}"
                for r in sorted(tested, key=lambda r: r["f1"], reverse=True)
            ]
            prompt += f"""
CHURN WINDOW TEST:
{chr(10).join(window_lines)}
Selected: {churn_window_result['selected_window']} days
"""

    prompt += f"""
Row count: {profile['row_count']}

Tasks:
1. Hypothesize the business type. Provide confidence (0-1) and reasoning. Reference specific findings from the analysis.

2. Generate 3-5 MCQs. These questions will be shown to a business user (not a data scientist).
   First, infer the business type from the data analysis above. Then tailor questions to THAT business.

   PURPOSE: The answers directly control which behavioral features we compute. Each question must map to a feature decision:
   - Product variety vs repeat buying → controls basket_diversity, product_mix_change features
   - Multi-channel vs single channel → controls channel_diversity feature
   - Geographic spread vs local → controls region_loyalty feature
   - How long before a customer is "gone" → controls churn window (days of inactivity)
   - Seasonal patterns → controls peak_vs_offpeak_ratio feature

   Write questions in plain business language. The user should not know these map to features.
   Questions must reflect what you see in the actual field names and values above.

   NEVER ask about: ML models, algorithms, evaluation metrics, feature selection, target variables, impact of churn, or anything technical.
   NEVER ask philosophical questions like "what is the impact of churn" — ask factual questions about buying behavior.

Return JSON with:
- "business_type": string
- "confidence": float
- "reasoning": string (reference specific findings)
- "questions": array of objects, each with:
  - "id": short snake_case identifier (e.g. "reorder_cycle")
  - "question": the question text (plain language, no jargon)
  - "options": array of objects, each with "label" (descriptive phrase the VP would recognize, e.g. "They reduce order size first") and "value" (short code, e.g. "reduce_size")
  - "context": why this question matters (internal note, not shown to user)

IMPORTANT: Each option "label" must be a descriptive phrase, NOT a letter like "A" or "B". Write questions a Sales VP would answer in 2 seconds."""

    if free_text:
        prompt += f"""

USER'S DOMAIN KNOWLEDGE:
{free_text}

Incorporate this into your hypothesis and questions."""

    return prompt
