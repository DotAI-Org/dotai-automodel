import pytest
import pandas as pd
import numpy as np

from app.agent.model_trainer import train_all_models, prepare_data, ModelResult


@pytest.fixture
def training_data():
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        "feature_a": np.random.randn(n),
        "feature_b": np.random.randn(n),
        "feature_c": np.random.randn(n) * 2,
    })
    # Labels correlated with feature_a
    y = pd.Series((X["feature_a"] + np.random.randn(n) * 0.5 > 0).astype(int))
    return X, y


@pytest.fixture
def split_data(training_data):
    X, y = training_data
    return prepare_data(X, y)


class TestPrepareData:
    def test_returns_five_elements(self, training_data):
        X, y = training_data
        result = prepare_data(X, y)
        assert len(result) == 5

    def test_drops_constant_columns(self, training_data):
        X, y = training_data
        X["constant"] = 1.0
        X_train, X_test, y_train, y_test, feature_names = prepare_data(X, y)
        assert "constant" not in feature_names

    def test_fills_nan(self, training_data):
        X, y = training_data
        X.iloc[0, 0] = np.nan
        X_train, X_test, y_train, y_test, feature_names = prepare_data(X, y)
        assert not X_train.isna().any().any()

    def test_raises_on_all_constant(self):
        X = pd.DataFrame({"a": [1] * 50, "b": [2] * 50})
        y = pd.Series([0] * 25 + [1] * 25)
        with pytest.raises(ValueError, match="No features"):
            prepare_data(X, y)


class TestTrainAllModels:
    def test_returns_two_models(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        assert len(results) == 2

    def test_sorted_by_auc_descending(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        aucs = [r.metrics["auc"] for r in results]
        assert aucs == sorted(aucs, reverse=True)

    def test_model_names(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        names = {r.name for r in results}
        assert names == {"xgboost", "random_forest"}

    def test_metrics_keys(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        for r in results:
            assert set(r.metrics.keys()) == {"auc", "precision", "recall", "f1"}
            for v in r.metrics.values():
                assert 0 <= v <= 1

    def test_confusion_matrix_keys(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        for r in results:
            assert set(r.confusion_matrix.keys()) == {"TP", "FP", "TN", "FN"}

    def test_feature_importance_length(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        for r in results:
            assert len(r.feature_importance) == len(feature_names)

    def test_training_time_positive(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        for r in results:
            assert r.training_time >= 0

    def test_model_objects_stored(self, split_data):
        X_train, X_test, y_train, y_test, feature_names = split_data
        results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
        for r in results:
            assert r.model is not None
            assert hasattr(r.model, "predict")
