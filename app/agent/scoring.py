def composite_score(metrics: dict) -> float:
    return (
        metrics.get("auc", 0) * 0.3
        + metrics.get("f1", 0) * 0.3
        + metrics.get("precision", 0) * 0.2
        + metrics.get("recall", 0) * 0.2
    )
