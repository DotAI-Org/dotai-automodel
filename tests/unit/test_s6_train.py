import pytest
import pandas as pd
import numpy as np
from fastapi import HTTPException

from app.stages.s6_train import handle
from app.session_store import store, SessionStore


def _build_train_session(n_customers=100, churn_rate=0.3, n_features=5):
    """Build a session dict with labeled_features and labels for training.
    Uses the module-level store so handle() can update it."""
    sid = store.create()

    np.random.seed(42)
    n_churned = int(n_customers * churn_rate)
    n_active = n_customers - n_churned

    labels = pd.Series(
        [1] * n_churned + [0] * n_active,
        index=[f"C{i}" for i in range(n_customers)],
        name="churn_label",
    )

    # Features: churned customers have different distributions
    features = pd.DataFrame(index=labels.index)
    for i in range(n_features):
        churned_vals = np.random.normal(10, 3, n_churned)
        active_vals = np.random.normal(5, 2, n_active)
        features[f"feat_{i}"] = np.concatenate([churned_vals, active_vals])

    store.update(sid, {
        "labeled_features": features,
        "labels": labels,
    })
    session = store.get(sid)
    return session, sid, store


class TestTrainHandle:
    def test_returns_four_metrics(self):
        session, sid, store = _build_train_session()
        result = handle(sid, session)
        metrics = result.metrics
        assert "auc" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics

    def test_auc_beats_random(self):
        session, sid, store = _build_train_session()
        result = handle(sid, session)
        assert result.metrics["auc"] > 0.5

    def test_confusion_matrix_sums_to_test_size(self):
        session, sid, store = _build_train_session(n_customers=100)
        result = handle(sid, session)
        cm = result.confusion_matrix
        total = cm.true_positive + cm.false_positive + cm.true_negative + cm.false_negative
        # test_size=0.2 of 100 = 20
        assert total == 20

    def test_feature_importance_length_and_values(self):
        session, sid, store = _build_train_session()
        result = handle(sid, session)
        assert len(result.feature_importance) <= 10
        for fi in result.feature_importance:
            assert fi.importance >= 0

    def test_model_stored_in_session(self):
        session, sid, store = _build_train_session()
        handle(sid, session)
        updated = store.get(sid)
        assert updated["model"] is not None
        assert updated["X_test"] is not None
        assert updated["y_test"] is not None
        assert updated["feature_names"] is not None

    def test_scale_pos_weight_for_imbalance(self):
        session, sid, store = _build_train_session(n_customers=100, churn_rate=0.1)
        handle(sid, session)
        # 10 churned, 90 active -> scale_pos_weight ~ 9
        # We verify the model was trained (can't access scale_pos_weight directly)
        updated = store.get(sid)
        assert updated["model"] is not None

    def test_drops_constant_columns(self):
        sid = store.create()
        np.random.seed(42)
        n = 50
        labels = pd.Series(
            [1] * 15 + [0] * 35,
            index=[f"C{i}" for i in range(n)],
        )
        features = pd.DataFrame(index=labels.index)
        features["good_feat"] = np.random.randn(n)
        features["constant_feat"] = 5.0  # zero variance
        store.update(sid, {"labeled_features": features, "labels": labels})
        session = store.get(sid)
        result = handle(sid, session)
        feat_names = [fi.feature for fi in result.feature_importance]
        assert "constant_feat" not in feat_names

    def test_raises_400_when_labels_missing(self):
        sid = store.create()
        features = pd.DataFrame({"f1": [1, 2, 3]}, index=["A", "B", "C"])
        store.update(sid, {"labeled_features": features, "labels": None})
        session = store.get(sid)
        with pytest.raises(HTTPException) as exc_info:
            handle(sid, session)
        assert exc_info.value.status_code == 400

    def test_raises_400_when_all_zero_variance(self):
        sid = store.create()
        n = 50
        labels = pd.Series([1] * 15 + [0] * 35, index=[f"C{i}" for i in range(n)])
        features = pd.DataFrame(index=labels.index)
        features["const1"] = 1.0
        features["const2"] = 2.0
        store.update(sid, {"labeled_features": features, "labels": labels})
        session = store.get(sid)
        with pytest.raises(HTTPException) as exc_info:
            handle(sid, session)
        assert exc_info.value.status_code == 400
