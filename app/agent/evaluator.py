import logging
from typing import Any

from app.models.schemas import LLMEvaluationOutput
from app.agent.model_trainer import ModelResult
from app.agent.scoring import composite_score
from app.llm.client import generate_structured

logger = logging.getLogger(__name__)

SUCCESS_CRITERIA = {
    "min_auc": 0.7,
    "min_f1": 0.5,
    "max_top_feature_importance": 0.50,
    "min_features_above_5pct": 3,
}


def check_rules(
    model_results: list[ModelResult],
    criteria: dict | None = None,
) -> dict:
    """Rule-based checks against success criteria. Returns dict with pass/fail and details."""
    criteria = criteria or SUCCESS_CRITERIA
    issues = []
    passed = True

    best = max(model_results, key=lambda r: composite_score(r.metrics)) if model_results else None
    if not best:
        return {"passed": False, "issues": ["No models trained"]}

    # Check AUC
    if best.metrics["auc"] < criteria["min_auc"]:
        issues.append(f"AUC {best.metrics['auc']} below minimum {criteria['min_auc']}")
        passed = False

    # Check F1
    if best.metrics["f1"] < criteria["min_f1"]:
        issues.append(f"F1 {best.metrics['f1']} below minimum {criteria['min_f1']}")
        passed = False

    # Check single feature dominance
    if best.feature_importance:
        top_imp = best.feature_importance[0]["importance"]
        if top_imp > criteria["max_top_feature_importance"]:
            issues.append(
                f"Top feature '{best.feature_importance[0]['feature']}' "
                f"has importance {top_imp} > {criteria['max_top_feature_importance']}"
            )
            passed = False

    # Check feature diversity
    if best.feature_importance:
        threshold = 0.05
        above_threshold = sum(
            1 for fi in best.feature_importance if fi["importance"] >= threshold
        )
        if above_threshold < criteria["min_features_above_5pct"]:
            issues.append(
                f"Only {above_threshold} features above 5% importance, "
                f"need at least {criteria['min_features_above_5pct']}"
            )
            passed = False

    return {"passed": passed, "issues": issues}


async def evaluate(
    model_results: list[ModelResult],
    feature_definitions: dict[str, str] | None = None,
    churn_label_info: str = "",
    iteration_history: list[dict] | None = None,
    criteria: dict | None = None,
) -> LLMEvaluationOutput:
    """Evaluate model results using rule-based checks + LLM judgment."""
    criteria = criteria or SUCCESS_CRITERIA
    rule_check = check_rules(model_results, criteria)

    # Build LLM prompt
    models_text = ""
    for r in model_results:
        top_features = r.feature_importance[:10] if r.feature_importance else []
        feat_text = "\n".join(
            f"    - {fi['feature']}: {fi['importance']}"
            for fi in top_features
        )
        models_text += f"""
Model: {r.name}
  AUC: {r.metrics['auc']}, Precision: {r.metrics['precision']}, Recall: {r.metrics['recall']}, F1: {r.metrics['f1']}
  Confusion Matrix: TP={r.confusion_matrix['TP']}, FP={r.confusion_matrix['FP']}, TN={r.confusion_matrix['TN']}, FN={r.confusion_matrix['FN']}
  Top Features:
{feat_text}
"""

    feature_defs_text = ""
    if feature_definitions:
        feature_defs_text = "\n".join(
            f"- {name}: {desc}" for name, desc in feature_definitions.items()
        )

    history_text = ""
    if iteration_history:
        for h in iteration_history:
            history_text += f"\nIteration {h.get('iteration', '?')}: "
            history_text += f"Features removed: {h.get('features_removed', [])}, "
            history_text += f"Features added: {h.get('features_added', [])}"

    rule_issues_text = "\n".join(f"- {i}" for i in rule_check["issues"]) if rule_check["issues"] else "None"

    prompt = f"""You are evaluating churn prediction model results for data leakage and quality.

MODEL RESULTS:
{models_text}

FEATURE DEFINITIONS:
{feature_defs_text or "Not provided"}

CHURN LABEL DEFINITION:
{churn_label_info or "Not provided"}

ITERATION HISTORY:
{history_text or "First iteration"}

RULE-BASED CHECK RESULTS:
Passed: {rule_check['passed']}
Issues:
{rule_issues_text}

LEAKAGE DETECTION HEURISTICS:
1. Single feature dominance: One feature > 50% importance
2. Perfect metrics: AUC > 0.99 with any single feature > 30% importance
3. Tautological features: Feature definition overlaps with label definition (e.g. recency measures "days since last purchase" and churn label means "no purchase in last N days")
4. Semantic overlap: If a feature measures something equivalent to the churn label (e.g., days since last purchase when churn = no purchase in N days), flag as leakage regardless of importance %

Evaluate:
1. Is there data leakage? Which features are suspect?
2. Is the model quality acceptable given the criteria?
3. Which model is best?
4. What adjustments should be made for the next iteration?

Return JSON with:
- leakage_detected: bool
- suspect_features: list of feature names to remove
- leakage_reasoning: explanation
- quality_acceptable: bool (true if rule checks pass AND no leakage)
- best_model: "xgboost" or "random_forest"
- suggested_adjustments: list of adjustment descriptions
- reasoning: explanation"""

    try:
        result = await generate_structured(prompt, LLMEvaluationOutput)
    except Exception as e:
        logger.error(f"LLM evaluation failed: {e}")
        # Fall back to rule-based evaluation only
        best_name = max(model_results, key=lambda r: composite_score(r.metrics)).name if model_results else "xgboost"
        result = LLMEvaluationOutput(
            leakage_detected=not rule_check["passed"],
            suspect_features=[],
            leakage_reasoning="LLM evaluation unavailable, using rule-based checks only",
            quality_acceptable=rule_check["passed"],
            best_model=best_name,
            suggested_adjustments=[f"Rule issue: {i}" for i in rule_check["issues"]],
            reasoning="Fallback to rule-based evaluation",
        )

    return result
