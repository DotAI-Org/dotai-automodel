import logging
from typing import Any

from app.models.schemas import DSLFeature, LLMFeatureSuggestionOutput
from app.llm.client import generate_structured

logger = logging.getLogger(__name__)

DSL_OPERATIONS_DOC = """
Available DSL operations:

1. aggregate: Per-customer aggregation
   params_json: {"column": "amount", "func": "mean|sum|count|max|min|std|median|nunique"}

2. aggregate_window: Aggregation within time window
   params_json: {"column": "amount", "func": "sum", "window_days": 30}

3. ratio: Ratio of two aggregations
   params_json: {"numerator": {"column": "amount", "func": "sum", "window_days": 30}, "denominator": {"column": "amount", "func": "sum"}}

4. trend: First-half vs second-half comparison
   params_json: {"column": "quantity", "func": "mean"}

5. conditional_count: Count rows matching condition
   params_json: {"column": "amount", "condition": "> 50"}

6. nunique: Distinct count per customer
   params_json: {"column": "product"}

7. gap_stat: Statistic on inter-purchase gaps
   params_json: {"func": "max|min|mean|std|median"}
"""


async def suggest_dsl_features(
    data_profile: dict,
    col_map: dict,
    hypothesis: dict | None = None,
    existing_features: list[str] | None = None,
    iteration_metrics: dict | None = None,
    excluded_features: list[str] | None = None,
) -> list[DSLFeature]:
    """Ask the LLM to suggest new DSL features based on context."""
    existing_features = existing_features or []
    excluded_features = excluded_features or []

    columns_text = "\n".join(
        f"- {role} -> {name}" for role, name in col_map.items()
    )

    existing_text = "\n".join(f"- {f}" for f in existing_features) if existing_features else "None"
    excluded_text = "\n".join(f"- {f}" for f in excluded_features) if excluded_features else "None"

    metrics_text = ""
    if iteration_metrics:
        metrics_text = f"""
Current model metrics:
  AUC: {iteration_metrics.get('auc', 'N/A')}
  F1: {iteration_metrics.get('f1', 'N/A')}
  Precision: {iteration_metrics.get('precision', 'N/A')}
  Recall: {iteration_metrics.get('recall', 'N/A')}
"""

    hypothesis_text = ""
    if hypothesis:
        h = hypothesis.get("hypothesis", hypothesis)
        hypothesis_text = f"Business type: {h.get('type', 'unknown')}\nReasoning: {h.get('reasoning', '')}"

    prompt = f"""You are a data scientist designing features for a churn prediction model.

DATA COLUMNS:
{columns_text}

BUSINESS CONTEXT:
{hypothesis_text or "Not provided"}

FEATURES ALREADY COMPUTED:
{existing_text}

FEATURES EXCLUDED (do not suggest these):
{excluded_text}

{metrics_text}

{DSL_OPERATIONS_DOC}

Suggest 2-5 new features using the DSL operations above. Each feature should:
1. Not duplicate existing features
2. Not be in the excluded list
3. Use columns that exist in the data
4. Have a clear description of what it measures and why it helps predict churn

For the "column" param, use the role name (e.g. "amount", "product") not the raw column name.

Return JSON with:
- suggested_features: list of features, each with name, description, operation, params_json (as a JSON string)
- reasoning: why these features help"""

    try:
        result = await generate_structured(prompt, LLMFeatureSuggestionOutput)
        # Filter out any features with names matching excluded list
        filtered = [
            f for f in result.suggested_features
            if f.name not in excluded_features and f.name not in existing_features
        ]
        return filtered
    except Exception as e:
        logger.error(f"Feature suggestion failed: {e}")
        return []
