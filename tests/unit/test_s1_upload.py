import pytest
import pandas as pd
import numpy as np
import io

from app.stages.s1_upload import _build_profile, _infer_dtype


class TestInferDtype:
    def test_numeric_series(self):
        s = pd.Series([1, 2, 3, 4, 5])
        assert _infer_dtype(s) == "numeric"

    def test_datetime_series(self):
        s = pd.Series(pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]))
        assert _infer_dtype(s) == "datetime"

    def test_categorical_series(self):
        # Low unique ratio + few unique values -> categorical
        s = pd.Series(["A", "B", "A", "B"] * 50)
        assert _infer_dtype(s) == "categorical"

    def test_text_series(self):
        # Many unique values -> text
        s = pd.Series([f"text_{i}" for i in range(200)])
        assert _infer_dtype(s) == "text"

    def test_all_null_series(self):
        s = pd.Series([None, None, None])
        result = _infer_dtype(s)
        # All-null should still return a type without crashing
        assert result in ("numeric", "datetime", "categorical", "text")


class TestBuildProfile:
    def test_column_count(self):
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["x", "y", "z"],
            "c": [1.1, 2.2, 3.3],
        })
        profile = _build_profile(df)
        assert len(profile.columns) == 3

    def test_row_count(self):
        df = pd.DataFrame({"a": range(50)})
        profile = _build_profile(df)
        assert profile.row_count == 50

    def test_sample_rows_max_5(self):
        df = pd.DataFrame({"a": range(100)})
        profile = _build_profile(df)
        assert len(profile.sample_rows) <= 5
