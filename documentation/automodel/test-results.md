# Churn-Tool Test Suite: Implementation Report

## Overview

Built a pytest-based test suite for the churn-tool module covering unit tests, edge case tests, and integration tests. The churn-tool has an 8-stage pipeline (upload, column mapping, hypothesis, features, labels, train, results, inference). Prior to this work, only two test files existed — both used `requests` against a live server with no quality assertions.

---

## Test Run Results

```
$ cd churn-tool && venv/bin/python -m pytest tests/unit/ -v
84 passed, 54 warnings in 3.69s

$ cd churn-tool && venv/bin/python -m pytest tests/edge/ -v
10 passed, 17 warnings in 0.96s

$ cd churn-tool && venv/bin/python -m pytest -m "not llm" -v
94 passed, 1 failed (pre-existing), 13 skipped, 71 warnings in 4.97s
```

The 1 failure is the pre-existing `test_pipeline.py` which requires a running server on `localhost:8000`. The 13 skipped are integration tests requiring `GEMINI_API_KEY`.

---

## Files Created

### Foundation

| File | Purpose |
|------|---------|
| `churn-tool/pytest.ini` | Marker definitions (`llm`, `slow`), test path config |
| `churn-tool/tests/conftest.py` | Shared fixtures, marker auto-skip, data loading |
| `churn-tool/tests/unit/__init__.py` | Package init |
| `churn-tool/tests/integration/__init__.py` | Package init |
| `churn-tool/tests/edge/__init__.py` | Package init |
| `churn-tool/tests/generators/__init__.py` | Package init |

### Unit Tests (84 tests across 8 files)

| File | Tests | What It Covers |
|------|-------|----------------|
| `tests/unit/test_session_store.py` | 9 | `SessionStore` CRUD, TTL expiration, cleanup |
| `tests/unit/test_s1_upload.py` | 8 | `_infer_dtype()` for numeric/datetime/categorical/text/null, `_build_profile()` column count, row count, sample rows |
| `tests/unit/test_s4_tier1_features.py` | 15 | All 10 Tier 1 compute functions: recency, frequency (30d/60d/90d), monetary (total/avg), frequency trend, monetary trend, days between purchases (avg/std) |
| `tests/unit/test_s4_tier2_features.py` | 16 | All 12 Tier 2 compute functions + `_build_col_map()` and `_get_available_tier2()` helpers |
| `tests/unit/test_s5_labels.py` | 10 | `_get_churn_window()` (MCQ keys, auto-derive, clamping to [14, 365], fallback 90), `handle()` labeling logic |
| `tests/unit/test_s6_train.py` | 9 | XGBoost training: 4 metrics returned, AUC > 0.5, confusion matrix sums, feature importance, model stored in session, constant column dropping, error handling |
| `tests/unit/test_s8_inference.py` | 8 | Prediction count matches feature matrix, tier counts sum, 3 SHAP features per prediction, probability range [0,1], CSV download format |
| `tests/unit/test_risk_tiers.py` | 7 | `_get_risk_tier()` boundary tests: 0.71->High, 0.50->Medium, 0.30->Low, 0.70->Medium, 0.40->Low, 0.0->Low, 1.0->High |

### Edge Case Tests (10 tests)

| File | Tests | What It Covers |
|------|-------|----------------|
| `tests/generators/generate_edge_case_data.py` | N/A | 7 generator functions: `make_empty_df`, `make_single_customer`, `make_all_churned`, `make_all_active`, `make_single_day`, `make_negative_amounts`, `make_wide_csv` |
| `tests/edge/test_edge_cases.py` | 10 | Empty CSV produces empty features; single customer raises on train; all-churned/all-active raises on train (single class); single-day transactions produce NaN gaps without crash; negative amounts don't crash monetary features; non-CSV upload returns 400; invalid session ID returns 404; stage called out of order returns 400 |

### Integration Tests (13 tests, require GEMINI_API_KEY)

| File | Tests | What It Covers |
|------|-------|----------------|
| `tests/integration/test_pipeline_ecommerce.py` | 9 | E2E using `ecommerce_sample.csv`: upload profile (5000 rows, 8 cols), column mapping confidence > 0.7, hypothesis questions (4-8), feature count >= 10, churn rate 0.1-0.6, AUC >= 0.65, F1 >= 0.3, all 3 tiers have >= 1 user, CSV download has 201 lines |
| `tests/integration/test_pipeline_maturity.py` | 4 | E2E using `maturity_churn.csv`: >= 90% CHURN_ customers flagged High, >= 80% HEALTHY_ customers flagged Low, AUC >= 0.8, churn rate 0.3-0.7 |

---

## Bug Fix During Implementation

### Problem: `store.update()` writes to module-level singleton

The `handle()` functions in `s5_labels`, `s6_train`, and `s8_inference` all call `store.update(session_id, data)` where `store` is the module-level singleton imported from `app.session_store`. The initial test code created local `SessionStore()` instances and set up sessions there, but when `handle()` ran, it called `store.update()` on the singleton — writing data to a different store instance than the one the test was reading from.

**Symptom:** `KeyError: 'labels'` and `KeyError: 'model'` when reading session data after `handle()` returned.

**Fix:** Changed all test code to use the module-level singleton (`from app.session_store import store`) instead of creating local `SessionStore()` instances. Applied to:
- `tests/conftest.py` (fixtures `ecommerce_labels`, `trained_session`)
- `tests/unit/test_s5_labels.py` (TestHandle class)
- `tests/unit/test_s6_train.py` (`_build_train_session` and individual tests)
- `tests/unit/test_s8_inference.py` (error case tests)
- `tests/edge/test_edge_cases.py` (`_build_session_through_labels`)

---

## Run Commands

```bash
# Unit tests (no API key needed)
cd churn-tool && venv/bin/python -m pytest tests/unit/ -v

# Edge case tests (no API key needed)
cd churn-tool && venv/bin/python -m pytest tests/edge/ -v

# All non-LLM tests
cd churn-tool && venv/bin/python -m pytest -m "not llm" -v

# Integration tests (requires GEMINI_API_KEY)
GEMINI_API_KEY=xxx venv/bin/python -m pytest tests/integration/ -v -m llm

# Full suite
GEMINI_API_KEY=xxx venv/bin/python -m pytest -v
```

---

## Warnings

All 54+ warnings are `DeprecationWarning` from pandas about `DataFrameGroupBy.apply` operating on grouping columns. These originate from the production code in `s4_features.py` and `s5_labels.py`, not from the tests. They can be addressed separately by adding `include_groups=False` to the `.apply()` calls.
