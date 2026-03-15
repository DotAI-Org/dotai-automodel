"""Composite scoring function for model comparison."""


def composite_score(metrics: dict) -> float:
    """Compute a weighted score from AUC, F1, precision, and recall."""
    return (
        metrics.get("auc", 0) * 0.3
        + metrics.get("f1", 0) * 0.3
        + metrics.get("precision", 0) * 0.2
        + metrics.get("recall", 0) * 0.2
    )
