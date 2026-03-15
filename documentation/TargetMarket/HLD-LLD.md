# HLD + LLD: Multi-Data-Type Pipeline with Exhaustive Field Analysis

## High-Level Design

### Current State

```
Upload CSV → Column Map (LLM) → Hypothesis (LLM guess + MCQs) → Features (Tier1 + Tier2 + DSL) → Labels → Train (XGB+RF) → Results (LLM) → Inference (SHAP)
```

Single-file, transaction-only. LLM guesses business type. MCQs gate feature selection. One model. One entity type.

### Target State

```
Upload (multi-file + file_type tags)
  → Column Map (type-aware LLM, extended roles)
    → Exhaustive Field Analysis (4 analyses × every field → signature + feature matrix)
      → Auto Churn Window (6 candidates, pick best F1)
        → LLM Hypothesis (grounded in computed facts)
          → Show Findings (user confirms or corrects)
            → Statistical Pruning + Leakage Detection (3-layer)
              → Train (Model A baseline + Model B enriched + Model C/D/E if applicable)
                → Results (multi-source attribution, lift comparison)
                  → Inference (multi-source SHAP, action recommendations)
```

Multi-file, 5 data types, exhaustive computation, multiple models, feature group attribution.

### Architecture Changes

| Layer | Current | Target |
|-------|---------|--------|
| Upload | 1 file, no type tag | N files, each tagged with file_type (radio) + connection description |
| Column Mapping | 9 roles | ~34 roles (9 base + 25 type-specific) |
| Feature Computation | Tier 1 (10) + Tier 2 (12) + DSL per iteration | Exhaustive field analysis (one pass, ~80 features) + cross-source features |
| Label | Global churn window from MCQ or 2x median gap | Auto-selected from 6 candidates via fast XGBoost |
| Training | 1 model (XGB), agent loop tries RF | Model A (txn-only) + Model B (enriched) + Model C/D/E per data type |
| Evaluation | Name-based leakage check | 3-layer: statistical (AUC >0.90) + temporal ordering + ablation |
| Results | Single model metrics | Multi-model comparison, feature group attribution by tier |
| Frontend | MCQs for business context | Computed findings with confirm/correct flow |

### Data Flow Diagram

```
                    ┌──────────────┐
                    │  User Upload  │
                    │  N files +    │
                    │  file_type +  │
                    │  connections  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Stage 2:     │
                    │  Column Map   │──→ col_map per file
                    │  (type-aware) │    + join strategy
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Stage 3a:    │──→ Output 1: data_signature (per-field stats)
                    │  Exhaustive   │──→ Output 2: feature_matrix (per-customer)
                    │  Field        │
                    │  Analysis     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
       │ 3b: Auto    │ │ 3c: LLM │ │ 3d: Show    │
       │ Churn Window│ │Hypothesis│ │ Findings    │
       │ (6 tests)   │ │(grounded)│ │ (user       │
       └──────┬──────┘ └──┬──────┘ │  confirms)  │
              │            │        └──┬──────────┘
              └────────────┼───────────┘
                           │
                    ┌──────▼───────┐
                    │  Stage 4:     │
                    │  Pruning +    │──→ Leakage-free feature matrix
                    │  Leakage      │    (30-50 features)
                    │  Detection    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
       │ Model A     │ │ Model B │ │ Model C/D/E │
       │ (txn-only)  │ │(enriched)│ │ (per type)  │
       └──────┬──────┘ └──┬──────┘ └──┬──────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼───────┐
                    │  Results:     │
                    │  Comparison + │──→ Lift, attribution, backtest
                    │  Attribution  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Inference:   │
                    │  Multi-source │──→ Names, risk, multi-source "what changed"
                    │  SHAP         │
                    └──────────────┘
```

### New Files

| File | Purpose |
|------|---------|
| `app/stages/s3_field_analysis.py` | Exhaustive field analysis engine (4 analyses per dtype) |
| `app/stages/s3_churn_window.py` | Auto churn window selection (6 candidates) |
| `app/stages/s4_pruning.py` | Statistical pruning + leakage detection (3-layer) |
| `app/stages/s4_cross_source.py` | Cross-file feature computation |
| `app/features/tier3_service.py` | Service/warranty features (15) |
| `app/features/tier3_loyalty.py` | Loyalty/membership features (18) |
| `app/features/tier3_returns.py` | Returns/delivery features (15) |
| `app/features/tier3_field.py` | Field interaction features (16) |
| `app/features/tier3_master.py` | Master data features (6) |

### Modified Files

| File | Changes |
|------|---------|
| `app/stages/s1_upload.py` | Accept `file_type` per file, store in session |
| `app/stages/s2_column_map.py` | Extended roles, type-aware prompt, cross-file summary |
| `app/stages/s3_hypothesis.py` | Replace MCQ-first flow with findings-first flow |
| `app/stages/s4_features.py` | Receive pre-computed matrix from 3a, add cross-source + interaction features |
| `app/stages/s5_labels.py` | Compound labels, multi-entity labels, auto-selected window |
| `app/stages/s6_train.py` | Multi-model training (A/B/C/D/E), feature group tracking |
| `app/stages/s7_results.py` | Multi-model comparison, tier attribution, lift reporting |
| `app/stages/s8_inference.py` | Multi-source SHAP, action recommendations, entity-specific output |
| `app/models/schemas.py` | New schemas for file_type, extended roles, multi-model results, findings |
| `app/agent/loop.py` | Multi-model orchestration, exhaustive analysis integration |
| `app/agent/evaluator.py` | 3-layer leakage detection replaces name-based check |
| `app/db/models.py` | detected_data_types, multi-model storage, engagement_predictions |
| `app/persistence.py` | Persist field analysis signature, multi-model results |
| `app/main.py` | New endpoints for findings confirmation, field analysis status |
| `static/index.html` | Per-file radio selector, findings screen, model comparison, multi-source explanations |

### Database Schema Changes

```sql
-- Existing sessions table additions
ALTER TABLE sessions ADD COLUMN detected_data_types JSONB;  -- ["type1", "type3"]
ALTER TABLE sessions ADD COLUMN field_analysis_signature JSONB;  -- per-field stats
ALTER TABLE sessions ADD COLUMN churn_window_results JSONB;  -- all 6 window test results
ALTER TABLE sessions ADD COLUMN selected_churn_window INT;  -- auto-selected window days
ALTER TABLE sessions ADD COLUMN model_comparison JSONB;  -- {model_a: {}, model_b: {}, ...}
ALTER TABLE sessions ADD COLUMN feature_tier_map JSONB;  -- {feature_name: tier_number}

-- Existing session_files table additions
ALTER TABLE session_files ADD COLUMN file_type VARCHAR(20);  -- transaction, service, loyalty, returns, field, master, other
ALTER TABLE session_files ADD COLUMN connection_description TEXT;
ALTER TABLE session_files ADD COLUMN user_description TEXT;
```

---

## LLD: Stage 1 — Upload

### Current Implementation (`app/stages/s1_upload.py`)

- `handle(file, user_id)` — single file → parse CSV, build profile, create session
- `handle_multi(files, description, user_id)` — N files → parse each, store list of `{filename, df, profile}`, store description

### Changes

**1.1. New request schema for multi-upload**

```python
# app/models/schemas.py — additions

class FileMetadata(BaseModel):
    filename: str
    file_type: str  # "transaction" | "service" | "loyalty" | "returns" | "field" | "master" | "other"
    user_description: str = ""  # optional free-text
    connection_description: str = ""  # how this file connects to others

class MultiUploadRequest(BaseModel):
    file_metadata: list[FileMetadata]
    # files come as UploadFile[], metadata comes as Form JSON
```

**1.2. Modified `handle_multi()` function**

```python
# s1_upload.py changes

async def handle_multi(
    files: list[UploadFile],
    file_metadata_json: str,  # JSON string of list[FileMetadata]
    user_id: str,
) -> MultiUploadResponse:
    file_metadata = [FileMetadata(**m) for m in json.loads(file_metadata_json)]

    dataframes = []
    for file, meta in zip(files, file_metadata):
        df = _parse_csv(file)
        profile = _build_profile(df)
        dataframes.append({
            "filename": file.filename,
            "df": df,
            "profile": profile,
            "file_type": meta.file_type,           # NEW
            "user_description": meta.user_description,  # NEW
            "connection_description": meta.connection_description,  # NEW
        })

    session_id = _generate_session_id()
    store.create(session_id, {
        "dataframes": dataframes,
        "user_id": user_id,
        "stage": 1,
    })

    # Persist file_type in session_files table
    await _persist_files(session_id, dataframes)

    return MultiUploadResponse(
        session_id=session_id,
        files=[{
            "filename": d["filename"],
            "rows": len(d["df"]),
            "columns": len(d["df"].columns),
            "file_type": d["file_type"],
        } for d in dataframes],
    )
```

**1.3. Validation per file type**

```python
def _validate_file_type(df: pd.DataFrame, profile: dict, file_type: str) -> list[str]:
    """Return list of warnings if declared file_type does not match data."""
    warnings = []

    if file_type == "transaction":
        has_date = any(c["dtype"] == "datetime" for c in profile["columns"])
        has_numeric = any(c["dtype"] == "numeric" for c in profile["columns"])
        if not has_date:
            warnings.append("Transaction file has no date column.")
        if not has_numeric:
            warnings.append("Transaction file has no numeric amount column.")

    elif file_type == "service":
        # Expect at least: an ID column, a date column
        has_date = any(c["dtype"] == "datetime" for c in profile["columns"])
        if not has_date:
            warnings.append("Service file has no date column for ticket dates.")

    elif file_type == "loyalty":
        # Expect a numeric column (points)
        has_numeric = any(c["dtype"] == "numeric" for c in profile["columns"])
        if not has_numeric:
            warnings.append("Loyalty file has no numeric column for points.")

    elif file_type == "returns":
        has_date = any(c["dtype"] == "datetime" for c in profile["columns"])
        if not has_date:
            warnings.append("Returns file has no date column.")

    elif file_type == "field":
        has_date = any(c["dtype"] == "datetime" for c in profile["columns"])
        if not has_date:
            warnings.append("Field visit file has no date column.")

    return warnings
```

**1.4. Endpoint change in `main.py`**

```python
@api_router.post("/sessions/multi", response_model=MultiUploadResponse)
async def create_session_multi(
    files: list[UploadFile] = File(...),
    file_metadata: str = Form(...),  # JSON string, replaces `description`
    user: dict = Depends(get_current_user),
):
    return await s1_upload.handle_multi(files, file_metadata, user_id=user["id"])
```

**1.5. DB persistence**

```python
# app/persistence.py — update save_session_files
async def save_session_files(db, session_id, dataframes):
    for d in dataframes:
        sf = SessionFile(
            session_id=session_id,
            filename=d["filename"],
            profile=d["profile"],
            dataframe_blob=compress_pickle(d["df"]),
            file_type=d.get("file_type", "other"),           # NEW
            connection_description=d.get("connection_description", ""),  # NEW
            user_description=d.get("user_description", ""),   # NEW
        )
        db.add(sf)
```

---

## LLD: Stage 2 — Column Mapping

### Current Implementation (`app/stages/s2_column_map.py`)

- `handle()` — sends column profiles to LLM, gets role assignments
- Roles: `customer_id`, `transaction_date`, `amount`, `product`, `quantity`, `category`, `channel`, `region`, `other`
- `join_files()` — LLM determines join strategy for multi-file
- `handle_with_feedback()` — user corrects mapping

### Changes

**2.1. Extended role enum**

```python
# app/models/schemas.py

# Current roles
BASE_ROLES = [
    "customer_id", "transaction_date", "amount", "product",
    "quantity", "category", "channel", "region", "other"
]

# New roles per data type
SERVICE_ROLES = [
    "ticket_id", "ticket_date", "resolution_date", "complaint_category",
    "warranty_status", "csat_score", "tat_days"
]

LOYALTY_ROLES = [
    "member_id", "points_earned", "points_redeemed", "tier",
    "enrollment_date", "transaction_type"
]

RETURNS_ROLES = [
    "return_id", "return_date", "return_reason", "return_quantity",
    "original_invoice"
]

FIELD_ROLES = [
    "visit_id", "visit_date", "entity_type", "visit_duration",
    "order_booked", "objective"
]

MASTER_ROLES = [
    "dealer_code", "dealer_name", "registration_date", "status",
    "credit_limit", "tier", "territory"
]

def get_roles_for_file_type(file_type: str) -> list[str]:
    """Return applicable roles based on file type."""
    roles = list(BASE_ROLES)
    type_map = {
        "service": SERVICE_ROLES,
        "loyalty": LOYALTY_ROLES,
        "returns": RETURNS_ROLES,
        "field": FIELD_ROLES,
        "master": MASTER_ROLES,
    }
    if file_type in type_map:
        roles.extend(type_map[file_type])
    elif file_type == "other":
        # Include all roles so LLM can match
        for r in type_map.values():
            roles.extend(r)
    return roles
```

**2.2. Type-aware LLM prompt**

```python
# s2_column_map.py — modified _build_prompt()

def _build_prompt(profile: dict, file_type: str = None, user_description: str = None) -> str:
    roles = get_roles_for_file_type(file_type or "transaction")

    prompt = f"""Map each column to one of these roles: {', '.join(roles)}

Column profiles:
{_format_profiles(profile)}
"""

    if file_type and file_type != "transaction":
        prompt += f"""
The user described this file as: {file_type} data.
{f'Additional context: {user_description}' if user_description else ''}
Prioritize roles matching {file_type} data."""

    return prompt
```

**2.3. Cross-file summary generation**

```python
# s2_column_map.py — new function

async def generate_cross_file_summary(session_id: str, session: dict) -> dict:
    """After mapping all files, produce a summary of detected types and join strategy."""
    dataframes = session["dataframes"]
    file_types = [d["file_type"] for d in dataframes]

    # Determine detected data types (Type 1-5)
    detected_types = _detect_data_types(file_types)

    # Build summary for LLM
    file_summaries = []
    for d in dataframes:
        mapping = session.get(f"column_mapping_{d['filename']}", session.get("column_mapping", {}))
        file_summaries.append({
            "filename": d["filename"],
            "file_type": d["file_type"],
            "row_count": len(d["df"]),
            "column_roles": mapping,
            "connection": d.get("connection_description", ""),
        })

    # LLM generates human-readable summary
    summary = await _llm_cross_file_summary(file_summaries, detected_types)

    # Store in session
    session["detected_data_types"] = detected_types
    session["cross_file_summary"] = summary
    store.update(session_id, session)

    return {
        "detected_types": detected_types,
        "summary": summary,
        "files": file_summaries,
    }

def _detect_data_types(file_types: list[str]) -> list[int]:
    """Map file_type tags to Type 1-5."""
    types = {1}  # Transaction is always present (base)
    type_map = {
        "service": 2,
        "loyalty": 3,
        "returns": 4,
        "field": 5,
    }
    for ft in file_types:
        if ft in type_map:
            types.add(type_map[ft])
    return sorted(types)
```

**2.4. Modified `handle()` — per-file mapping**

```python
async def handle(session_id: str, session: dict) -> ColumnMappingResponse:
    dataframes = session.get("dataframes", [])

    if not dataframes:
        # Single file path (existing)
        return await _handle_single(session_id, session)

    # Multi-file: map each file with its file_type context
    all_mappings = {}
    for d in dataframes:
        mapping = await _map_single_file(
            profile=d["profile"],
            file_type=d.get("file_type", "transaction"),
            user_description=d.get("user_description", ""),
        )
        all_mappings[d["filename"]] = mapping

    session["column_mappings"] = all_mappings  # per-file mappings
    session["column_mapping"] = all_mappings.get(dataframes[0]["filename"], {})  # primary file

    # Generate cross-file summary
    cross_summary = await generate_cross_file_summary(session_id, session)

    # Join files if multiple
    if len(dataframes) > 1:
        await join_files(session_id, session)

    store.update(session_id, session)
    return ColumnMappingResponse(
        column_mapping=session["column_mapping"],
        cross_file_summary=cross_summary.get("summary"),
        detected_types=cross_summary.get("detected_types"),
    )
```

**2.5. New endpoint for cross-file summary**

```python
# main.py — new endpoint
@api_router.get("/sessions/{session_id}/cross-file-summary")
async def cross_file_summary(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return {
        "detected_types": session.get("detected_data_types", [1]),
        "summary": session.get("cross_file_summary", ""),
    }
```

---

## LLD: Stage 3 — Hypothesis (Exhaustive Field Analysis + Auto Window + Findings)

### Current Implementation (`app/stages/s3_hypothesis.py`)

- `handle()` — LLM receives column roles + sample values, generates hypothesis + MCQs
- `_build_prompt()` — formats column names, roles, date range, sample rows
- Output: `{business_type, confidence, reasoning, questions[]}`

### Changes — This stage is rewritten into 5 substages

**3.1. New module: `app/stages/s3_field_analysis.py`**

This is the core computation engine. One pass through the data produces both the data signature (for LLM) and the per-customer feature matrix (for training).

```python
import pandas as pd
import numpy as np
from scipy import stats

def analyze_all_fields(
    df: pd.DataFrame,
    col_map: dict,          # {column_name: role}
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,  # optional, for univariate churn signal
) -> tuple[dict, pd.DataFrame]:
    """
    Run 4 analyses per field based on dtype.

    Returns:
        signature: dict of per-field statistics
        feature_matrix: DataFrame indexed by customer_id
    """
    signature = {}
    all_features = {}

    for col_name, role in col_map.items():
        if col_name == customer_id_col:
            continue

        dtype = _infer_analysis_dtype(df[col_name])

        if dtype == "numeric":
            sig, feats = analyze_numeric(
                df, col_name, customer_id_col, date_col, labels
            )
        elif dtype == "categorical":
            sig, feats = analyze_categorical(
                df, col_name, customer_id_col, date_col, labels
            )
        elif dtype == "datetime":
            sig, feats = analyze_datetime(
                df, col_name, customer_id_col
            )
        else:  # text
            sig = {"dtype": "text", "cardinality": df[col_name].nunique()}
            feats = {}

        signature[col_name] = {**sig, "role": role}
        all_features.update(feats)

    # Build feature matrix
    feature_matrix = pd.DataFrame(all_features)
    feature_matrix.index.name = "customer_id"

    return signature, feature_matrix


def analyze_numeric(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a numeric field."""
    col = df[col_name].dropna()
    features = {}

    # Analysis 1: Distribution (signature only)
    sig = {
        "dtype": "numeric",
        "mean": float(col.mean()),
        "median": float(col.median()),
        "std": float(col.std()),
        "skew": float(col.skew()),
        "p25": float(col.quantile(0.25)),
        "p75": float(col.quantile(0.75)),
        "outlier_pct": float((np.abs(col - col.mean()) > 3 * col.std()).mean() * 100),
    }

    # Analysis 2: Per-customer profile (signature + features)
    grouped = df.groupby(customer_id_col)[col_name]
    per_cust_mean = grouped.mean()
    per_cust_std = grouped.std().fillna(0)

    features[f"{col_name}_mean"] = per_cust_mean
    features[f"{col_name}_std"] = per_cust_std

    sig["per_customer_mean_of_means"] = float(per_cust_mean.mean())
    sig["per_customer_std_of_means"] = float(per_cust_mean.std())

    # Analysis 3: Univariate churn signal (signature only)
    if labels is not None:
        aligned = per_cust_mean.reindex(labels.index).dropna()
        aligned_labels = labels.reindex(aligned.index).dropna()
        common = aligned.index.intersection(aligned_labels.index)
        if len(common) > 20:
            from sklearn.metrics import roc_auc_score
            try:
                auc = roc_auc_score(aligned_labels[common], aligned[common])
                sig["univariate_churn_auc"] = float(auc)
            except ValueError:
                sig["univariate_churn_auc"] = None

    # Analysis 4: Temporal trend (feature)
    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        valid = dates.notna()
        if valid.sum() > 0:
            mid = dates[valid].quantile(0.5)
            first_half = df[valid & (dates <= mid)]
            second_half = df[valid & (dates > mid)]

            first_means = first_half.groupby(customer_id_col)[col_name].mean()
            second_means = second_half.groupby(customer_id_col)[col_name].mean()

            trend = second_means.subtract(first_means, fill_value=0)
            features[f"{col_name}_trend"] = trend
            sig["trend_direction"] = "increasing" if trend.mean() > 0 else "decreasing"

    return sig, features


def analyze_categorical(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
    date_col: str = None,
    labels: pd.Series = None,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a categorical field."""
    features = {}

    # Analysis 1: Concentration (signature only)
    vc = df[col_name].value_counts(normalize=True).head(5)
    sig = {
        "dtype": "categorical",
        "top_5": {str(k): round(float(v) * 100, 1) for k, v in vc.items()},
        "unique_count": int(df[col_name].nunique()),
        "long_tail_pct": round(float(1 - vc.sum()) * 100, 1),
    }

    # Analysis 2: Per-customer diversity (feature)
    diversity = df.groupby(customer_id_col)[col_name].nunique()
    features[f"{col_name}_diversity"] = diversity
    sig["avg_diversity_per_customer"] = float(diversity.mean())

    # Analysis 3: Churn rate by value (feature)
    if labels is not None:
        # For each customer, find their most frequent value
        mode_per_customer = df.groupby(customer_id_col)[col_name].agg(
            lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None
        )
        # Compute churn rate per value
        value_churn_rates = {}
        for val in df[col_name].dropna().unique():
            customers_with_val = mode_per_customer[mode_per_customer == val].index
            common = customers_with_val.intersection(labels.index)
            if len(common) >= 5:
                value_churn_rates[str(val)] = float(labels[common].mean())

        sig["churn_rate_by_value"] = value_churn_rates

        # Feature: the churn rate of the customer's most-frequent value
        churn_rate_map = {v: r for v, r in value_churn_rates.items()}
        features[f"{col_name}_churn_rate"] = mode_per_customer.map(
            lambda x: churn_rate_map.get(str(x), 0)
        )

    # Analysis 4: Temporal shift (feature)
    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        valid = dates.notna()
        if valid.sum() > 0:
            mid = dates[valid].quantile(0.5)

            def jaccard_shift(group):
                group_dates = dates[group.index]
                first = set(group[group_dates <= mid].dropna())
                second = set(group[group_dates > mid].dropna())
                if not first and not second:
                    return 0
                union = first | second
                if len(union) == 0:
                    return 0
                return 1 - len(first & second) / len(union)

            shift = df[valid].groupby(customer_id_col)[col_name].apply(jaccard_shift)
            features[f"{col_name}_shift"] = shift

    return sig, features


def analyze_datetime(
    df: pd.DataFrame,
    col_name: str,
    customer_id_col: str,
) -> tuple[dict, dict[str, pd.Series]]:
    """4 analyses for a datetime field."""
    features = {}
    dates = pd.to_datetime(df[col_name], errors="coerce")
    max_date = dates.max()

    # Analysis 1: Recency (feature)
    last_per_customer = df.assign(_dt=dates).groupby(customer_id_col)["_dt"].max()
    recency = (max_date - last_per_customer).dt.days
    features[f"{col_name}_recency"] = recency

    sig = {
        "dtype": "datetime",
        "min": str(dates.min()),
        "max": str(dates.max()),
        "recency_median": float(recency.median()),
        "recency_p25": float(recency.quantile(0.25)),
        "recency_p75": float(recency.quantile(0.75)),
    }

    # Analysis 2: Frequency (feature)
    for window_days in [30, 60, 90]:
        cutoff = max_date - pd.Timedelta(days=window_days)
        freq = df[dates >= cutoff].groupby(customer_id_col).size()
        freq = freq.reindex(last_per_customer.index, fill_value=0)
        features[f"{col_name}_frequency_{window_days}d"] = freq

    sig["frequency_30d_median"] = float(features[f"{col_name}_frequency_30d"].median())

    # Analysis 3: Gap profile (feature)
    def compute_gaps(group):
        group_dates = pd.to_datetime(group, errors="coerce").dropna().sort_values()
        if len(group_dates) < 2:
            return pd.Series({
                "gap_avg": np.nan, "gap_std": np.nan,
                "gap_max": np.nan, "gap_cv": np.nan
            })
        gaps = group_dates.diff().dt.days.dropna()
        avg = gaps.mean()
        return pd.Series({
            "gap_avg": avg,
            "gap_std": gaps.std(),
            "gap_max": gaps.max(),
            "gap_cv": gaps.std() / avg if avg > 0 else np.nan,
        })

    gap_stats = df.groupby(customer_id_col)[col_name].apply(compute_gaps)
    if isinstance(gap_stats, pd.DataFrame):
        for stat in ["gap_avg", "gap_std", "gap_max", "gap_cv"]:
            features[f"{col_name}_{stat}"] = gap_stats[stat]

    sig["gap_median"] = float(features.get(f"{col_name}_gap_avg", pd.Series([0])).median())

    # Analysis 4: Seasonality (signature only)
    monthly = dates.dt.month.value_counts().sort_index()
    avg_monthly = monthly.mean()
    if avg_monthly > 0:
        seasonal_index = (monthly / avg_monthly).to_dict()
        sig["seasonal_index"] = {str(k): round(float(v), 2) for k, v in seasonal_index.items()}
        sig["is_seasonal"] = any(v > 1.3 or v < 0.7 for v in seasonal_index.values())

    return sig, features


def analyze_cross_file(
    df_primary: pd.DataFrame,
    df_secondary: pd.DataFrame,
    primary_customer_col: str,
    secondary_customer_col: str,
    secondary_file_type: str,
    labels: pd.Series = None,
) -> tuple[dict, pd.DataFrame]:
    """Compute cross-file signatures and features."""
    sig = {}
    features = {}

    # Overlap rate
    primary_customers = set(df_primary[primary_customer_col].unique())
    secondary_customers = set(df_secondary[secondary_customer_col].unique())
    overlap = primary_customers & secondary_customers
    sig["overlap_rate"] = round(len(overlap) / len(primary_customers) * 100, 1) if primary_customers else 0
    sig["overlap_count"] = len(overlap)

    # Type-specific cross-file analysis
    # (computed after per-file feature matrices are built)

    return sig, pd.DataFrame(features)


def _infer_analysis_dtype(series: pd.Series) -> str:
    """Determine dtype for analysis purposes."""
    if pd.api.types.is_numeric_dtype(series):
        if series.nunique() < 10:
            return "categorical"
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    # Try parsing as datetime
    try:
        pd.to_datetime(series.dropna().head(20))
        return "datetime"
    except (ValueError, TypeError):
        pass
    if series.nunique() / max(len(series), 1) > 0.5:
        return "text"
    return "categorical"
```

**3.2. New module: `app/stages/s3_churn_window.py`**

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import xgboost as xgb

CANDIDATE_WINDOWS = [30, 60, 90, 120, 180, 365]

def auto_select_churn_window(
    df: pd.DataFrame,
    feature_matrix: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
) -> dict:
    """
    Test 6 churn windows, return the one with best F1.

    Returns:
        {
            "selected_window": int,
            "all_results": [{"window": int, "f1": float, "churn_rate": float}, ...],
            "adaptive_gap": pd.Series,  # per-customer gap_vs_personal_median
        }
    """
    dates = pd.to_datetime(df[date_col], errors="coerce")
    max_date = dates.max()

    results = []

    for window in CANDIDATE_WINDOWS:
        cutoff = max_date - pd.Timedelta(days=window)

        # Generate labels
        last_purchase = df.groupby(customer_id_col)[date_col].max()
        last_purchase = pd.to_datetime(last_purchase)
        labels = (last_purchase < cutoff).astype(int)

        # Check churn rate
        churn_rate = labels.mean()
        if churn_rate < 0.05 or churn_rate > 0.80:
            results.append({
                "window": window,
                "f1": None,
                "churn_rate": round(float(churn_rate), 3),
                "status": "discarded",
            })
            continue

        # Align feature matrix with labels
        common = feature_matrix.index.intersection(labels.index)
        if len(common) < 50:
            continue

        X = feature_matrix.loc[common].fillna(0)
        y = labels.loc[common]

        # Fast XGBoost
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            model = xgb.XGBClassifier(
                n_estimators=50, max_depth=4, learning_rate=0.1,
                scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
                use_label_encoder=False, eval_metric="logloss",
                verbosity=0,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            f1 = f1_score(y_test, y_pred, zero_division=0)
        except Exception:
            f1 = 0

        results.append({
            "window": window,
            "f1": round(float(f1), 3),
            "churn_rate": round(float(churn_rate), 3),
            "status": "tested",
        })

    # Pick best
    tested = [r for r in results if r.get("f1") is not None]
    if tested:
        best = max(tested, key=lambda r: r["f1"])
        selected = best["window"]
    else:
        selected = 90  # fallback

    # Compute adaptive gap feature
    last_purchase = df.groupby(customer_id_col)[date_col].apply(
        lambda x: pd.to_datetime(x).max()
    )
    median_gap = df.groupby(customer_id_col)[date_col].apply(
        lambda x: pd.to_datetime(x).sort_values().diff().dt.days.median()
    )
    current_gap = (max_date - last_purchase).dt.days
    adaptive_gap = current_gap / median_gap.replace(0, np.nan)

    return {
        "selected_window": selected,
        "all_results": results,
        "adaptive_gap": adaptive_gap,
    }
```

**3.3. Modified `app/stages/s3_hypothesis.py`**

```python
# Revised handle() — findings-first flow

async def handle(session_id: str, session: dict, free_text: str = None) -> HypothesisResponse:
    df = session["df"]
    col_map = session["column_mapping"]
    customer_id_col = _get_col(col_map, "customer_id")
    date_col = _get_col(col_map, "transaction_date")

    # 3a. Exhaustive field analysis
    from app.stages.s3_field_analysis import analyze_all_fields
    preliminary_labels = _generate_preliminary_labels(df, customer_id_col, date_col, window=90)
    signature, feature_matrix = analyze_all_fields(
        df, col_map, customer_id_col, date_col, labels=preliminary_labels
    )
    session["field_analysis_signature"] = signature
    session["feature_matrix"] = feature_matrix

    # 3b. Auto churn window
    from app.stages.s3_churn_window import auto_select_churn_window
    window_result = auto_select_churn_window(
        df, feature_matrix, customer_id_col, date_col
    )
    session["churn_window_days"] = window_result["selected_window"]
    session["churn_window_results"] = window_result["all_results"]

    # Recompute labels with selected window
    final_labels = _generate_preliminary_labels(
        df, customer_id_col, date_col, window=window_result["selected_window"]
    )

    # Recompute univariate AUCs with correct labels
    signature = _recompute_univariate_aucs(signature, feature_matrix, final_labels)
    session["field_analysis_signature"] = signature

    # Add adaptive gap as a feature
    feature_matrix["gap_vs_personal_median"] = window_result["adaptive_gap"]
    session["feature_matrix"] = feature_matrix
    session["labels"] = final_labels

    # 3c. LLM hypothesis grounded in computed facts
    hypothesis = await _build_grounded_hypothesis(signature, window_result, free_text)

    # 3d. Generate findings for user
    findings = _generate_findings(signature, window_result, session.get("detected_data_types", [1]))

    session["hypothesis"] = hypothesis
    session["findings"] = findings
    session["stage"] = 3
    store.update(session_id, session)

    return HypothesisResponse(
        hypothesis=hypothesis,
        findings=findings,
        churn_window=window_result,
        # MCQs only sent if user clicks "Let me correct"
        questions=_generate_mcqs_with_defaults(signature, window_result),
    )


def _generate_findings(signature: dict, window_result: dict, detected_types: list) -> dict:
    """Build the findings object shown to the user."""
    findings = {
        "purchase_pattern": {},
        "churn_threshold": {},
        "seasonality": {},
        "revenue_concentration": {},
        "signals": [],  # top 3-5 by univariate AUC
        "cross_file": {},
    }

    # Extract top signals (AUC > 0.55, sorted descending)
    signals = []
    for field_name, field_sig in signature.items():
        auc = field_sig.get("univariate_churn_auc")
        if auc and auc > 0.55 and field_sig.get("role") != "customer_id":
            signals.append({
                "field": field_name,
                "role": field_sig["role"],
                "auc": auc,
                "dtype": field_sig["dtype"],
                # Include type-specific context for LLM to rewrite
                "raw_stats": {k: v for k, v in field_sig.items()
                             if k not in ("dtype", "role")},
            })

    findings["signals"] = sorted(signals, key=lambda s: s["auc"], reverse=True)[:5]

    # Churn threshold
    findings["churn_threshold"] = {
        "selected_window": window_result["selected_window"],
        "all_results": window_result["all_results"],
    }

    return findings


async def _build_grounded_hypothesis(signature: dict, window_result: dict, free_text: str = None) -> dict:
    """LLM hypothesis with computed facts as input."""
    prompt = _format_signature_for_llm(signature, window_result)
    if free_text:
        prompt += f"\n\nUser context: {free_text}"

    # LLM call — returns structured hypothesis
    response = await llm_call(prompt, schema=HypothesisSchema)
    return response


def _generate_preliminary_labels(df, customer_id_col, date_col, window=90):
    """Generate labels with a given window for initial analysis."""
    dates = pd.to_datetime(df[date_col], errors="coerce")
    max_date = dates.max()
    cutoff = max_date - pd.Timedelta(days=window)
    last_purchase = df.groupby(customer_id_col)[date_col].apply(
        lambda x: pd.to_datetime(x).max()
    )
    return (last_purchase < cutoff).astype(int)
```

**3.4. New endpoint for findings confirmation**

```python
# main.py — new endpoints

@api_router.post("/sessions/{session_id}/findings/confirm")
async def confirm_findings(session_id: str, user: dict = Depends(get_current_user)):
    """User confirms computed findings — proceed to training."""
    session = await get_session_with_auth(session_id, user)
    session["findings_confirmed"] = True
    store.update(session_id, session)
    return {"status": "confirmed"}


@api_router.post("/sessions/{session_id}/findings/correct")
async def correct_findings(session_id: str, body: MCQAnswers, user: dict = Depends(get_current_user)):
    """User overrides via MCQs — recompute with corrections."""
    session = await get_session_with_auth(session_id, user)
    # Apply MCQ overrides (e.g., different churn window)
    overrides = _apply_mcq_overrides(session, body)
    session["mcq_answers"] = body.dict()
    session["findings_confirmed"] = True
    store.update(session_id, session)
    return {"status": "corrected", "overrides_applied": overrides}
```

**3.5. Schema additions**

```python
# app/models/schemas.py — additions

class Finding(BaseModel):
    field: str
    role: str
    auc: float
    dtype: str
    plain_language: str = ""  # LLM-rewritten version

class FindingsResponse(BaseModel):
    purchase_pattern: dict
    churn_threshold: dict
    seasonality: dict
    revenue_concentration: dict
    signals: list[Finding]
    cross_file: dict = {}

class HypothesisResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    hypothesis: dict
    findings: dict
    churn_window: dict
    questions: list[dict] = []  # MCQs with defaults, shown on "Let me correct"
```

---

## LLD: Stage 4 — Feature Engineering (Pruning + Leakage Detection)

### Current Implementation (`app/stages/s4_features.py`)

- `handle()` — computes Tier 1 (10 features) + Tier 2 (12 features, LLM-selected) + DSL features
- `compute_feature_matrix()` — builds feature matrix from raw df
- Output: feature_matrix (per-customer)

### Changes — Stage 4 receives pre-computed matrix from Stage 3

**4.1. New module: `app/stages/s4_pruning.py`**

```python
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score

def statistical_pruning(
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
) -> tuple[pd.DataFrame, dict]:
    """
    Remove noise features. Returns pruned matrix + report.

    Steps:
    1. Drop zero-variance features
    2. Drop features with >90% null
    3. Drop correlated features (keep higher AUC)
    """
    report = {"dropped": [], "kept": len(feature_matrix.columns)}
    X = feature_matrix.copy()

    # Step 1: Zero variance
    zero_var = X.columns[X.std() == 0]
    X = X.drop(columns=zero_var)
    report["dropped"].extend([{"feature": f, "reason": "zero_variance"} for f in zero_var])

    # Step 2: High null
    null_pct = X.isnull().mean()
    high_null = null_pct[null_pct > 0.90].index
    X = X.drop(columns=high_null)
    report["dropped"].extend([{"feature": f, "reason": "high_null"} for f in high_null])

    # Step 3: Correlation pruning
    X_filled = X.fillna(0)
    corr = X_filled.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

    to_drop = set()
    for col in upper.columns:
        correlated = upper.index[upper[col] > 0.95].tolist()
        for corr_col in correlated:
            if corr_col in to_drop or col in to_drop:
                continue
            # Keep the one with higher univariate AUC
            auc_col = _safe_auc(X_filled[col], labels)
            auc_corr = _safe_auc(X_filled[corr_col], labels)
            drop = corr_col if auc_col >= auc_corr else col
            to_drop.add(drop)
            report["dropped"].append({
                "feature": drop,
                "reason": f"correlated_with_{col if drop == corr_col else corr_col}",
            })

    X = X.drop(columns=list(to_drop))
    report["kept"] = len(X.columns)

    return X, report


def _safe_auc(feature: pd.Series, labels: pd.Series) -> float:
    """Compute AUC, return 0.5 on failure."""
    common = feature.index.intersection(labels.index)
    if len(common) < 20:
        return 0.5
    try:
        return roc_auc_score(labels[common], feature[common])
    except (ValueError, TypeError):
        return 0.5


def leakage_detection(
    feature_matrix: pd.DataFrame,
    labels: pd.Series,
    col_map: dict,
    date_col: str = None,
    df: pd.DataFrame = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Three-layer leakage detection.

    Returns:
        cleaned feature_matrix, leakage report
    """
    report = {"suspects": [], "removed": [], "kept_as_leading": []}

    # Layer 1: Statistical detection — AUC > 0.90
    suspects = []
    X = feature_matrix.fillna(0)
    for col in X.columns:
        auc = _safe_auc(X[col], labels)
        if auc > 0.90:
            suspects.append({"feature": col, "auc": round(auc, 3)})

    report["suspects"] = suspects

    if not suspects:
        return feature_matrix, report

    # Layer 2: Temporal ordering
    # For each suspect, check if the signal preceded churn
    to_remove = []
    for suspect in suspects:
        feat_name = suspect["feature"]

        # Check if this is a recency-type feature (datetime-derived)
        is_recency = "_recency" in feat_name
        is_frequency = "_frequency_" in feat_name

        if is_recency:
            # Recency features are tautological with churn labels
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "tautological_with_churn_label",
                "auc": suspect["auc"],
            })
        elif is_frequency:
            # Recent frequency may overlap with churn definition
            to_remove.append(feat_name)
            report["removed"].append({
                "feature": feat_name,
                "reason": "overlaps_with_churn_definition",
                "auc": suspect["auc"],
            })
        else:
            # Layer 3: Ablation test
            # Train with and without this feature
            from sklearn.model_selection import train_test_split
            import xgboost as xgb

            common = X.index.intersection(labels.index)
            X_common = X.loc[common]
            y_common = labels.loc[common]

            try:
                X_tr, X_te, y_tr, y_te = train_test_split(
                    X_common, y_common, test_size=0.2, random_state=42, stratify=y_common
                )

                # With feature
                model_with = xgb.XGBClassifier(
                    n_estimators=50, max_depth=4, verbosity=0,
                    use_label_encoder=False, eval_metric="logloss",
                )
                model_with.fit(X_tr, y_tr)
                auc_with = roc_auc_score(y_te, model_with.predict_proba(X_te)[:, 1])

                # Without feature
                X_tr_no = X_tr.drop(columns=[feat_name])
                X_te_no = X_te.drop(columns=[feat_name])
                model_without = xgb.XGBClassifier(
                    n_estimators=50, max_depth=4, verbosity=0,
                    use_label_encoder=False, eval_metric="logloss",
                )
                model_without.fit(X_tr_no, y_tr)
                auc_without = roc_auc_score(y_te, model_without.predict_proba(X_te_no)[:, 1])

                drop = auc_with - auc_without

                if drop > 0.15:
                    # Feature carries the model — suspicious
                    to_remove.append(feat_name)
                    report["removed"].append({
                        "feature": feat_name,
                        "reason": "carries_model_single_feature",
                        "auc": suspect["auc"],
                        "auc_drop": round(drop, 3),
                    })
                elif drop < 0.05:
                    # Redundant — safe to remove
                    to_remove.append(feat_name)
                    report["removed"].append({
                        "feature": feat_name,
                        "reason": "redundant_with_other_features",
                        "auc": suspect["auc"],
                        "auc_drop": round(drop, 3),
                    })
                else:
                    # Moderate impact — keep as potential leading indicator
                    report["kept_as_leading"].append({
                        "feature": feat_name,
                        "auc": suspect["auc"],
                        "auc_drop": round(drop, 3),
                    })

            except Exception:
                # On failure, remove conservatively
                to_remove.append(feat_name)
                report["removed"].append({
                    "feature": feat_name,
                    "reason": "ablation_failed",
                    "auc": suspect["auc"],
                })

    cleaned = feature_matrix.drop(columns=to_remove, errors="ignore")
    return cleaned, report
```

**4.2. New module: `app/stages/s4_cross_source.py`**

```python
import pandas as pd
import numpy as np

def compute_cross_source_features(
    primary_features: pd.DataFrame,   # per-customer features from transaction file
    secondary_features: pd.DataFrame, # per-customer features from secondary file
    secondary_type: str,              # "service", "loyalty", "returns", "field"
) -> pd.DataFrame:
    """
    Compute interaction features between primary and secondary data.
    Join on index (customer_id).
    """
    # Left join: primary customers as base
    combined = primary_features.join(secondary_features, how="left", rsuffix="_sec")
    cross_features = pd.DataFrame(index=combined.index)

    if secondary_type == "loyalty":
        # Engagement-purchase ratio
        if "points_earned_total" in secondary_features.columns:
            monetary = primary_features.get("amount_mean")
            if monetary is not None:
                cross_features["engagement_purchase_ratio"] = (
                    combined.get("points_earned_total", 0) /
                    monetary.replace(0, np.nan)
                )

    elif secondary_type == "service":
        # Service-to-purchase ratio
        if "ticket_id_mean" in secondary_features.columns or True:
            # Count service interactions vs purchase count
            pass  # computed from Tier 3 features

    elif secondary_type == "field":
        # Visit-to-order conversion
        pass

    return cross_features


def compute_interaction_features(
    feature_matrix: pd.DataFrame,
    signature: dict,
    labels: pd.Series,
) -> pd.DataFrame:
    """
    For pairs of features both with AUC > 0.60,
    compute ratio and product.
    """
    high_signal = []
    for field_name, field_sig in signature.items():
        auc = field_sig.get("univariate_churn_auc")
        if auc and auc > 0.60:
            # Find corresponding features in matrix
            for col in feature_matrix.columns:
                if col.startswith(field_name):
                    high_signal.append((col, auc))

    interactions = pd.DataFrame(index=feature_matrix.index)

    # Limit to top 5 to avoid combinatorial explosion
    high_signal = sorted(high_signal, key=lambda x: x[1], reverse=True)[:5]

    for i, (feat_a, _) in enumerate(high_signal):
        for feat_b, _ in high_signal[i+1:]:
            a = feature_matrix[feat_a].fillna(0)
            b = feature_matrix[feat_b].fillna(0)

            interactions[f"{feat_a}_x_{feat_b}_ratio"] = a / b.replace(0, np.nan)
            interactions[f"{feat_a}_x_{feat_b}_product"] = a * b

    return interactions
```

**4.3. Modified `app/stages/s4_features.py`**

```python
async def handle(session_id: str, session: dict, body: MCQAnswers = None) -> FeaturesResponse:
    """
    Stage 4 — receives pre-computed feature matrix from Stage 3.
    Adds cross-source features, prunes, detects leakage.
    """
    feature_matrix = session["feature_matrix"]  # from Stage 3a
    labels = session["labels"]  # from Stage 3b
    signature = session["field_analysis_signature"]
    detected_types = session.get("detected_data_types", [1])

    # 4a. Add cross-source features (if multi-file)
    if len(detected_types) > 1 and "secondary_features" in session:
        from app.stages.s4_cross_source import compute_cross_source_features
        for sec_type, sec_features in session["secondary_features"].items():
            cross = compute_cross_source_features(feature_matrix, sec_features, sec_type)
            feature_matrix = feature_matrix.join(cross)

    # Add interaction features
    from app.stages.s4_cross_source import compute_interaction_features
    interactions = compute_interaction_features(feature_matrix, signature, labels)
    feature_matrix = feature_matrix.join(interactions)

    # 4b. Statistical pruning
    from app.stages.s4_pruning import statistical_pruning
    feature_matrix, pruning_report = statistical_pruning(feature_matrix, labels)

    # 4c. Leakage detection
    from app.stages.s4_pruning import leakage_detection
    feature_matrix, leakage_report = leakage_detection(
        feature_matrix, labels, session["column_mapping"],
        date_col=_get_col(session["column_mapping"], "transaction_date"),
        df=session["df"],
    )

    # Tag features with tiers
    tier_map = _build_tier_map(feature_matrix.columns, session["column_mapping"], detected_types)

    session["feature_matrix"] = feature_matrix
    session["pruning_report"] = pruning_report
    session["leakage_report"] = leakage_report
    session["feature_tier_map"] = tier_map
    session["stage"] = 4
    store.update(session_id, session)

    return FeaturesResponse(
        features=list(feature_matrix.columns),
        feature_count=len(feature_matrix.columns),
        tier_distribution=_tier_distribution(tier_map),
        pruning_report=pruning_report,
        leakage_report=leakage_report,
    )


def _build_tier_map(columns, col_map, detected_types) -> dict:
    """Map each feature to its tier based on source column role."""
    tier_map = {}
    transaction_roles = {"customer_id", "transaction_date", "amount"}
    tier2_roles = {"product", "category", "channel", "region", "quantity"}
    secondary_roles = set()  # roles from secondary files

    for col in columns:
        # Determine source field from feature name prefix
        source_field = col.split("_mean")[0].split("_std")[0].split("_trend")[0].split("_diversity")[0]
        role = col_map.get(source_field, "other")

        if role in transaction_roles:
            tier_map[col] = 1
        elif role in tier2_roles:
            tier_map[col] = 2
        elif role in secondary_roles:
            tier_map[col] = 3
        elif "gap_vs_personal_median" in col or "_x_" in col:
            tier_map[col] = 3  # cross-source / computed
        else:
            tier_map[col] = 4  # "other" fields

    return tier_map
```

---

## LLD: Stage 5 — Label Generation

### Current Implementation (`app/stages/s5_labels.py`)

- `handle()` — computes binary churn labels from time-split
- `_get_churn_window()` — from MCQ answer or 2x median gap
- cutoff = max_date - window → label = 1 if last_purchase < cutoff

### Changes

**5.1. Labels already computed in Stage 3b**

Stage 5 now validates and optionally recomputes labels with user overrides.

```python
def handle(session_id: str, session: dict) -> LabelsResponse:
    """
    Labels were auto-selected in Stage 3b.
    Stage 5 validates, applies overrides, and computes compound labels.
    """
    # Labels from auto-selection
    labels = session.get("labels")
    churn_window = session.get("churn_window_days", 90)
    feature_matrix = session["feature_matrix"]

    # Apply MCQ override if user changed window
    if session.get("mcq_answers"):
        override_window = _extract_window_override(session["mcq_answers"])
        if override_window and override_window != churn_window:
            churn_window = override_window
            labels = _recompute_labels(session["df"], session["column_mapping"], churn_window)
            session["churn_window_days"] = churn_window

    # Compound labels for multi-type data
    detected_types = session.get("detected_data_types", [1])
    if len(detected_types) > 1:
        labels = _compute_compound_labels(
            session, labels, detected_types, churn_window
        )

    # Align
    common = feature_matrix.index.intersection(labels.index)
    labeled_features = feature_matrix.loc[common]
    aligned_labels = labels.loc[common]

    session["labels"] = aligned_labels
    session["labeled_features"] = labeled_features
    session["cutoff_date"] = str(
        pd.to_datetime(session["df"][_get_col(session["column_mapping"], "transaction_date")]).max()
        - pd.Timedelta(days=churn_window)
    )
    session["stage"] = 5
    store.update(session_id, session)

    return LabelsResponse(
        churn_window_days=churn_window,
        total_customers=len(aligned_labels),
        churned=int(aligned_labels.sum()),
        active=int((aligned_labels == 0).sum()),
        churn_rate=round(float(aligned_labels.mean()), 3),
    )


def _compute_compound_labels(session, base_labels, detected_types, window):
    """
    Compound labels: churn = no purchase AND no engagement.
    For Type 3 (loyalty): no purchase AND no points earned.
    For Type 2 (service): no purchase AND no service interactions.
    """
    compound = base_labels.copy()

    if 3 in detected_types:  # loyalty
        loyalty_features = session.get("secondary_features", {}).get("loyalty")
        if loyalty_features is not None and "points_earned_90d" in loyalty_features.columns:
            no_engagement = (loyalty_features["points_earned_90d"] == 0).astype(int)
            common = compound.index.intersection(no_engagement.index)
            # Churn = 1 only if BOTH no purchase AND no engagement
            # This reduces false positives for seasonal buyers with engagement
            compound.loc[common] = (compound.loc[common] & no_engagement.loc[common]).astype(int)

    return compound
```

**5.2. Multi-entity label support**

```python
def _compute_entity_labels(session, entity_type="dealer"):
    """
    Compute labels for different entity types.
    entity_type: "dealer" (default) or "influencer"
    """
    if entity_type == "influencer":
        # Use influencer activity as the basis for labels
        influencer_df = session.get("secondary_dfs", {}).get("loyalty")
        if influencer_df is not None:
            # Label: influencer who stopped earning points
            influencer_id_col = _get_col(session.get("secondary_col_maps", {}).get("loyalty", {}), "member_id")
            date_col = _get_col(session.get("secondary_col_maps", {}).get("loyalty", {}), "enrollment_date")
            # ... compute labels from influencer activity
            pass

    # Default: dealer labels from transaction data
    return session["labels"]
```

---

## LLD: Stage 6 — Model Training

### Current Implementation (`app/stages/s6_train.py`)

- `handle()` — fills NaN, drops zero-variance, 80/20 split, trains XGBoost
- Single model output

### Changes

**6.1. Multi-model training**

```python
from app.agent.model_trainer import train_models

def handle(session_id: str, session: dict) -> TrainResponse:
    """Train Model A (baseline) + Model B (enriched) + applicable C/D/E."""
    feature_matrix = session["labeled_features"]
    labels = session["labels"]
    tier_map = session.get("feature_tier_map", {})
    detected_types = session.get("detected_data_types", [1])

    results = {}

    # Model A: Transaction-only (Tier 1 + Tier 2)
    tier12_cols = [c for c in feature_matrix.columns if tier_map.get(c, 4) <= 2]
    if tier12_cols:
        results["model_a"] = _train_single(
            feature_matrix[tier12_cols], labels, "Model A (transactions)"
        )

    # Model B: Enriched (all tiers)
    results["model_b"] = _train_single(
        feature_matrix, labels, "Model B (enriched)"
    )

    # Model C: Engagement churn (Type 3 or 5 — Tier 3 features only)
    if 3 in detected_types or 5 in detected_types:
        tier3_cols = [c for c in feature_matrix.columns if tier_map.get(c, 4) == 3]
        if len(tier3_cols) >= 3:
            # Label: purchase decline >50% (different from binary churn)
            decline_labels = _compute_decline_labels(session)
            if decline_labels is not None:
                results["model_c"] = _train_single(
                    feature_matrix[tier3_cols].reindex(decline_labels.index).dropna(),
                    decline_labels,
                    "Model C (engagement risk)",
                )

    # Model D: Influencer-to-dealer propagation
    if 3 in detected_types and "influencer_features" in session:
        inf_features = session["influencer_features"]
        if len(inf_features.columns) >= 3:
            results["model_d"] = _train_single(
                inf_features.reindex(labels.index).fillna(0),
                labels,
                "Model D (influencer signals)",
            )

    # Model E: Service-driven (Type 2)
    if 2 in detected_types:
        service_cols = [c for c in feature_matrix.columns
                       if tier_map.get(c, 4) in (1, 2, 3)]
        if service_cols:
            results["model_e"] = _train_single(
                feature_matrix[service_cols], labels,
                "Model E (service-driven)",
            )

    # Select champion (highest F1 among A and B)
    champion = max(
        [r for k, r in results.items() if k in ("model_a", "model_b")],
        key=lambda r: r["metrics"]["f1"],
    )

    # Compute lift
    lift = None
    if "model_a" in results and "model_b" in results:
        lift = {
            "f1_baseline": results["model_a"]["metrics"]["f1"],
            "f1_enriched": results["model_b"]["metrics"]["f1"],
            "f1_lift": round(
                results["model_b"]["metrics"]["f1"] - results["model_a"]["metrics"]["f1"], 3
            ),
        }

    # Feature group attribution
    attribution = _compute_tier_attribution(champion, tier_map)

    session["model_comparison"] = results
    session["champion"] = champion
    session["lift"] = lift
    session["tier_attribution"] = attribution
    session["metrics"] = champion["metrics"]
    session["model"] = champion["model"]
    session["feature_importance"] = champion["feature_importance"]
    session["stage"] = 6
    store.update(session_id, session)

    return TrainResponse(
        champion_name=champion["name"],
        metrics=champion["metrics"],
        lift=lift,
        models_trained=list(results.keys()),
    )


def _train_single(X, y, name):
    """Train XGBoost + RF, return best."""
    X = X.fillna(0)

    # Drop zero-variance
    non_zero_var = X.columns[X.std() > 0]
    X = X[non_zero_var]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    import xgboost as xgb
    from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix

    model = xgb.XGBClassifier(
        n_estimators=100, max_depth=5, learning_rate=0.1,
        scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
        use_label_encoder=False, eval_metric="logloss", verbosity=0,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "auc": round(float(roc_auc_score(y_test, y_prob)), 3),
        "f1": round(float(f1_score(y_test, y_pred)), 3),
        "precision": round(float(precision_score(y_test, y_pred)), 3),
        "recall": round(float(recall_score(y_test, y_pred)), 3),
    }

    importance = dict(zip(X.columns, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])

    return {
        "name": name,
        "model": model,
        "metrics": metrics,
        "feature_importance": importance,
        "feature_names": list(X.columns),
        "X_test": X_test,
        "y_test": y_test,
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }


def _compute_tier_attribution(champion, tier_map):
    """Group feature importance by tier."""
    attribution = {1: 0, 2: 0, 3: 0, 4: 0}
    for feat, importance in champion["feature_importance"].items():
        tier = tier_map.get(feat, 4)
        attribution[tier] += importance

    total = sum(attribution.values()) or 1
    return {
        f"tier_{k}": round(v / total * 100, 1)
        for k, v in attribution.items()
    }
```

---

## LLD: Stage 7 — Results

### Current Implementation (`app/stages/s7_results.py`)

- `handle()` — combines metrics with LLM summary
- `_generate_summary()` — LLM writes business-language explanation
- Output: summary, metrics, feature_importance, sample_predictions

### Changes

**7.1. Multi-model comparison + tier attribution**

```python
async def handle(session_id: str, session: dict) -> ResultsResponse:
    champion = session["champion"]
    model_comparison = session.get("model_comparison", {})
    lift = session.get("lift")
    tier_attribution = session.get("tier_attribution", {})
    leakage_report = session.get("leakage_report", {})

    # LLM summary — enriched with multi-source context
    summary = await _generate_enriched_summary(
        champion=champion,
        lift=lift,
        tier_attribution=tier_attribution,
        leakage_report=leakage_report,
        detected_types=session.get("detected_data_types", [1]),
        findings=session.get("findings", {}),
    )

    # Backtest predictions — with multi-source "what changed"
    sample_predictions = _build_sample_predictions(
        session, champion, tier_map=session.get("feature_tier_map", {})
    )

    session["summary"] = summary
    session["stage"] = 7
    store.update(session_id, session)

    return ResultsResponse(
        summary=summary,
        metrics=champion["metrics"],
        feature_importance=champion["feature_importance"],
        sample_predictions=sample_predictions,
        model_comparison={k: v["metrics"] for k, v in model_comparison.items()},
        lift=lift,
        tier_attribution=tier_attribution,
    )


async def _generate_enriched_summary(
    champion, lift, tier_attribution, leakage_report, detected_types, findings
):
    """LLM generates summary with multi-source context."""
    prompt = f"""Generate a summary for a Sales VP:

Model performance: {champion['metrics']}
Feature importance: {champion['feature_importance']}

"""
    if lift:
        prompt += f"""
Data enrichment impact:
- Baseline (transactions only): F1 = {lift['f1_baseline']}
- Enriched (all data sources): F1 = {lift['f1_enriched']}
- Lift: +{lift['f1_lift']}
"""

    prompt += f"""
Signal attribution by source:
{tier_attribution}

Key findings from data analysis:
{findings.get('signals', [])}

Leakage checks performed:
- Suspects found: {len(leakage_report.get('suspects', []))}
- Removed: {len(leakage_report.get('removed', []))}
- Kept as leading indicators: {len(leakage_report.get('kept_as_leading', []))}

Write a 3-5 sentence summary in plain language. No technical jargon. Focus on what the VP should do next."""

    return await llm_call(prompt)


def _build_sample_predictions(session, champion, tier_map):
    """Build sample predictions with multi-source 'what changed'."""
    model = champion["model"]
    X_test = champion["X_test"]
    y_test = champion["y_test"]

    probs = model.predict_proba(X_test)[:, 1]

    # SHAP for multi-source explanations
    import shap
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    predictions = []
    for idx, (customer_id, prob) in enumerate(zip(X_test.index[:20], probs[:20])):
        # Top 3 features by SHAP
        shap_row = shap_values[idx] if isinstance(shap_values, np.ndarray) else shap_values[1][idx]
        top_indices = np.argsort(np.abs(shap_row))[-3:][::-1]
        top_features = [
            {
                "feature": X_test.columns[i],
                "impact": float(shap_row[i]),
                "tier": tier_map.get(X_test.columns[i], 4),
                "value": float(X_test.iloc[idx, i]),
            }
            for i in top_indices
        ]

        predictions.append({
            "customer_id": str(customer_id),
            "churn_probability": round(float(prob), 3),
            "risk_tier": _get_risk_tier(prob),
            "actual": int(y_test.iloc[idx]) if idx < len(y_test) else None,
            "top_features": top_features,
        })

    return predictions
```

---

## LLD: Stage 8 — Inference

### Current Implementation (`app/stages/s8_inference.py`)

- `handle()` — runs model on full feature matrix, computes SHAP values
- `handle_download()` — CSV with predictions
- Output: per-customer predictions with top features

### Changes

**8.1. Multi-source SHAP + action recommendations**

```python
def handle(session_id: str, session: dict) -> InferenceResponse:
    model = session["model"]
    feature_matrix = session["feature_matrix"]
    tier_map = session.get("feature_tier_map", {})
    detected_types = session.get("detected_data_types", [1])

    X = feature_matrix[session.get("feature_names", feature_matrix.columns)].fillna(0)
    probs = model.predict_proba(X)[:, 1]

    # SHAP
    import shap
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    predictions = []
    for idx, (customer_id, prob) in enumerate(zip(X.index, probs)):
        shap_row = shap_values[idx] if isinstance(shap_values, np.ndarray) else shap_values[1][idx]
        top_indices = np.argsort(np.abs(shap_row))[-3:][::-1]

        top_features = []
        for i in top_indices:
            feat_name = X.columns[i]
            tier = tier_map.get(feat_name, 4)
            top_features.append({
                "feature": feat_name,
                "impact": float(shap_row[i]),
                "tier": tier,
                "source": _tier_to_source(tier),
                "value": float(X.iloc[idx, i]),
            })

        # Action recommendation based on top feature tiers
        action = _generate_action(top_features, detected_types)

        predictions.append({
            "customer_id": str(customer_id),
            "churn_probability": round(float(prob), 3),
            "risk_tier": _get_risk_tier(prob),
            "top_features": top_features,
            "action": action,
        })

    # Sort by probability descending
    predictions.sort(key=lambda p: p["churn_probability"], reverse=True)

    session["predictions"] = predictions
    session["stage"] = 8
    store.update(session_id, session)

    return InferenceResponse(predictions=predictions[:100])


def _tier_to_source(tier: int) -> str:
    return {1: "transaction", 2: "product/category", 3: "secondary_data", 4: "other_fields"}.get(tier, "unknown")


def _generate_action(top_features, detected_types):
    """Generate action recommendation based on top contributing features."""
    actions = []
    for feat in top_features:
        if feat["tier"] == 3:
            if 3 in detected_types:  # loyalty
                if "points" in feat["feature"] or "earn" in feat["feature"]:
                    actions.append("Check loyalty program engagement. Points activity has declined.")
                elif "tier" in feat["feature"]:
                    actions.append("Tier downgrade detected. Consider retention offer.")
            if 2 in detected_types:  # service
                if "ticket" in feat["feature"] or "csat" in feat["feature"]:
                    actions.append("Open service complaints. Resolve before expecting orders.")
                if "warranty" in feat["feature"]:
                    actions.append("Warranty expiring. Trigger renewal outreach.")
            if 5 in detected_types:  # field
                if "visit" in feat["feature"]:
                    actions.append("Rep visit frequency has dropped. Schedule visit.")
        elif feat["tier"] == 4:
            if "payment_terms" in feat["feature"]:
                actions.append("Review payment terms. Credit pressure may be a factor.")

    return actions[0] if actions else "Review account and schedule contact."


def handle_download(session_id: str, session: dict):
    """CSV download with multi-source columns."""
    predictions = session["predictions"]
    import io
    import csv

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "customer_id", "churn_probability", "risk_tier",
        "top_feature_1", "top_feature_1_source",
        "top_feature_2", "top_feature_2_source",
        "top_feature_3", "top_feature_3_source",
        "action",
    ])
    writer.writeheader()

    for p in predictions:
        row = {
            "customer_id": p["customer_id"],
            "churn_probability": p["churn_probability"],
            "risk_tier": p["risk_tier"],
            "action": p.get("action", ""),
        }
        for i, feat in enumerate(p.get("top_features", [])[:3]):
            row[f"top_feature_{i+1}"] = feat["feature"]
            row[f"top_feature_{i+1}_source"] = feat["source"]
        writer.writerow(row)

    output.seek(0)
    return output
```

---

## LLD: Agent Loop Changes

### Current Implementation (`app/agent/loop.py`)

- 5 iterations: compute features → align labels → train → evaluate → adjust
- Single model per iteration
- LLM evaluator checks for leakage by feature name

### Changes

**Agent loop integration with new pipeline:**

```python
async def run_agent(session_id: str, session: dict):
    """
    Revised agent loop:
    1. Run exhaustive field analysis (Stage 3a) — ONCE, not per iteration
    2. Auto-select churn window (Stage 3b) — ONCE
    3. Prune + leakage detect (Stage 4b/4c) — ONCE
    4. Train multiple models (Stage 6) — per iteration with DSL additions
    5. Evaluate — per iteration
    """
    state = get_agent_state(session_id)

    # Phase 1: One-time computation (not repeated per iteration)
    if state.iteration == 0:
        # 3a. Exhaustive field analysis
        await _broadcast(session_id, "agent_progress", {
            "step": "field_analysis",
            "message": f"Analyzing {len(session['column_mapping'])} fields...",
        })
        signature, feature_matrix = analyze_all_fields(
            session["df"], session["column_mapping"],
            _get_col(session["column_mapping"], "customer_id"),
            _get_col(session["column_mapping"], "transaction_date"),
        )
        session["field_analysis_signature"] = signature
        session["feature_matrix"] = feature_matrix

        # 3b. Auto churn window
        await _broadcast(session_id, "agent_progress", {
            "step": "churn_window",
            "message": "Testing 6 churn thresholds...",
        })
        window_result = auto_select_churn_window(
            session["df"], feature_matrix,
            _get_col(session["column_mapping"], "customer_id"),
            _get_col(session["column_mapping"], "transaction_date"),
        )
        session["churn_window_days"] = window_result["selected_window"]
        labels = _generate_labels(session, window_result["selected_window"])
        session["labels"] = labels

        # 4b + 4c. Prune + leakage detect
        await _broadcast(session_id, "agent_progress", {
            "step": "pruning",
            "message": "Removing noise and checking for data leakage...",
        })
        feature_matrix, _ = statistical_pruning(feature_matrix, labels)
        feature_matrix, _ = leakage_detection(feature_matrix, labels, session["column_mapping"])
        session["feature_matrix"] = feature_matrix

    # Phase 2: Iterative training (up to max_iterations)
    for i in range(state.iteration, state.max_iterations):
        state.iteration = i + 1

        # Check stop
        if state.user_overrides.get("stop"):
            state.status = "interrupted"
            break

        # Train models
        await _broadcast(session_id, "agent_progress", {
            "step": "training",
            "iteration": i + 1,
            "message": f"Training models (iteration {i+1})...",
        })

        # On iteration 1: train with exhaustive features
        # On iteration 2+: add DSL features from LLM suggestions
        current_features = session["feature_matrix"]
        if state.dsl_features:
            dsl_matrix = execute_dsl_features(state.dsl_features, session["df"])
            current_features = current_features.join(dsl_matrix, how="left")

        # Remove excluded features
        current_features = current_features.drop(
            columns=[f for f in state.excluded_features if f in current_features.columns],
            errors="ignore",
        )

        # Train
        results = _train_all_models(current_features, session["labels"], session)

        # Evaluate
        evaluation = await _evaluate(results, state, session)

        # Record iteration
        state.history.append({
            "iteration": i + 1,
            "models": {k: v["metrics"] for k, v in results.items()},
            "evaluation": evaluation,
        })

        await _broadcast(session_id, "iteration_result", state.history[-1])

        if evaluation.get("quality_acceptable") and not evaluation.get("leakage_detected"):
            champion = _select_champion(results)
            state.champion = champion
            state.status = "success"
            await _broadcast(session_id, "champion_selected", {
                "champion": champion["name"],
                "metrics": champion["metrics"],
            })
            break

        # Adjust for next iteration
        if evaluation.get("suspect_features"):
            state.excluded_features.extend(evaluation["suspect_features"])
        if evaluation.get("suggested_dsl"):
            state.dsl_features.extend(evaluation["suggested_dsl"])

    # Final: pick best if max iterations reached
    if state.status == "running":
        state.champion = _select_best_across_iterations(state.history, results)
        state.status = "completed"

    # Persist
    session["champion"] = state.champion
    session["metrics"] = state.champion["metrics"]
    session["model"] = state.champion["model"]
    store.update(session_id, session)
    set_agent_state(session_id, state)
    await _persist_agent_state(session_id, state)
```

---

## LLD: Frontend Changes

### Current Implementation (`static/index.html`)

Single-page app with screens:
1. Landing (pre-login)
2. Upload (drag-drop CSV)
3. Data summary
4. MCQ / business context
5. Agent progress (WebSocket)
6. Results (backtest, customer list, model details)
7. Download

### Changes

**F1. Upload Screen — Per-file type selector**

```html
<!-- After file drop, show per-file metadata panel -->
<div class="file-metadata-panel" id="fileMetadataPanel">
  <!-- Rendered dynamically per file -->
</div>

<script>
function renderFileMetadata(files) {
  const panel = document.getElementById('fileMetadataPanel');
  panel.innerHTML = files.map((file, i) => `
    <div class="file-card" data-index="${i}">
      <h4>${file.name} <span class="file-size">(${formatRows(file)} rows)</span></h4>

      <label>What is this file?</label>
      <div class="radio-group">
        ${['transaction', 'service', 'loyalty', 'returns', 'field', 'master', 'other']
          .map(type => `
            <label class="radio-option">
              <input type="radio" name="filetype-${i}" value="${type}"
                     ${type === 'transaction' && i === 0 ? 'checked' : ''}>
              <span>${FILE_TYPE_LABELS[type]}</span>
            </label>
          `).join('')}
      </div>

      <label>Optional: describe in your own words</label>
      <textarea class="file-description" placeholder="e.g., North region sales data, last 18 months"></textarea>

      ${files.length > 1 ? `
        <label>How does this file connect to the others?</label>
        <textarea class="file-connection"
          placeholder='e.g., "dealer_code in this file matches distributor_code in the sales file"'></textarea>
      ` : ''}
    </div>
  `).join('');
}

const FILE_TYPE_LABELS = {
  transaction: 'Transaction / purchase orders / invoices',
  service: 'Service / warranty / complaint records',
  loyalty: 'Loyalty / points / membership data',
  returns: 'Returns / damage / expiry records',
  field: 'Field visits / call reports / engagement logs',
  master: 'Customer / dealer master (profile data)',
  other: 'Other',
};

// On submit: collect metadata and send with files
async function uploadFiles(files) {
  const formData = new FormData();
  const metadata = [];

  files.forEach((file, i) => {
    formData.append('files', file);
    metadata.push({
      filename: file.name,
      file_type: document.querySelector(`input[name="filetype-${i}"]:checked`)?.value || 'other',
      user_description: document.querySelectorAll('.file-description')[i]?.value || '',
      connection_description: document.querySelectorAll('.file-connection')[i]?.value || '',
    });
  });

  formData.append('file_metadata', JSON.stringify(metadata));

  const res = await fetch('/api/sessions/multi', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  return res.json();
}
</script>
```

**F2. Findings Screen (replaces MCQ screen for primary flow)**

```html
<div class="findings-screen" id="findingsScreen" style="display:none">
  <h2>What we found in your data</h2>

  <div class="finding-section" id="purchasePattern">
    <!-- Populated from findings.purchase_pattern -->
  </div>

  <div class="finding-section" id="churnThreshold">
    <!-- "We tested 6 thresholds. 60 days produced the clearest signal." -->
  </div>

  <div class="finding-section" id="seasonality">
    <!-- Seasonal index visualization -->
  </div>

  <div class="finding-section" id="signals">
    <h3>Signals we found in your data</h3>
    <ul id="signalList">
      <!-- Populated from findings.signals -->
    </ul>
  </div>

  <div class="finding-section" id="crossFile" style="display:none">
    <!-- Cross-file findings, shown only for multi-file -->
  </div>

  <div class="findings-actions">
    <p>Does this match what you see?</p>
    <button class="btn-primary" onclick="confirmFindings()">Yes, continue</button>
    <button class="btn-secondary" onclick="showCorrections()">Let me correct</button>
  </div>

  <div class="free-text-section">
    <label>Anything else we should know?</label>
    <textarea id="additionalContext"
      placeholder='e.g., "We had a price increase in March that caused some dealers to hold off ordering"'>
    </textarea>
  </div>
</div>

<script>
function renderFindings(findings) {
  // Purchase pattern
  document.getElementById('purchasePattern').innerHTML = `
    <p><strong>Purchase pattern:</strong> ${findings.purchase_pattern.summary}</p>
  `;

  // Churn threshold
  const ct = findings.churn_threshold;
  document.getElementById('churnThreshold').innerHTML = `
    <p><strong>Churn threshold:</strong> Customers who go ${ct.selected_window} days without
    ordering are unlikely to return. We tested 6 thresholds and ${ct.selected_window} days
    produced the clearest signal.</p>
    <div class="window-results">
      ${ct.all_results.filter(r => r.status === 'tested').map(r => `
        <div class="window-chip ${r.window === ct.selected_window ? 'selected' : ''}">
          ${r.window}d: F1=${r.f1}
        </div>
      `).join('')}
    </div>
  `;

  // Signals
  document.getElementById('signalList').innerHTML = findings.signals.map(s => `
    <li class="signal-item">
      <span class="signal-auc">AUC ${s.auc.toFixed(2)}</span>
      <span class="signal-text">${s.plain_language || s.field}</span>
    </li>
  `).join('');

  document.getElementById('findingsScreen').style.display = 'block';
}

async function confirmFindings() {
  await fetch(`/api/sessions/${sessionId}/findings/confirm`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  // Proceed to agent/training
  startAgent();
}

function showCorrections() {
  // Show MCQ panel with defaults pre-filled from findings
  document.getElementById('mcqPanel').style.display = 'block';
}
</script>
```

**F3. Results Screen — Model Comparison + Tier Attribution**

```html
<div class="model-comparison" id="modelComparison" style="display:none">
  <h3>Model Comparison</h3>
  <table class="comparison-table">
    <thead>
      <tr>
        <th>Model</th><th>F1</th><th>AUC</th><th>Precision</th><th>Recall</th>
      </tr>
    </thead>
    <tbody id="comparisonBody">
    </tbody>
  </table>

  <div class="lift-banner" id="liftBanner" style="display:none">
    <!-- "Adding your loyalty data improved F1 from 0.82 to 0.91" -->
  </div>
</div>

<div class="tier-attribution" id="tierAttribution">
  <h3>Signal Sources</h3>
  <div class="attribution-bars" id="attributionBars">
    <!-- Horizontal stacked bar chart showing tier % -->
  </div>
</div>

<script>
function renderModelComparison(comparison, lift) {
  const tbody = document.getElementById('comparisonBody');
  tbody.innerHTML = Object.entries(comparison).map(([key, metrics]) => `
    <tr class="${key === 'model_b' ? 'champion-row' : ''}">
      <td>${key.replace('model_', 'Model ').toUpperCase()}</td>
      <td>${metrics.f1}</td>
      <td>${metrics.auc}</td>
      <td>${metrics.precision}</td>
      <td>${metrics.recall}</td>
    </tr>
  `).join('');

  if (lift && lift.f1_lift > 0) {
    document.getElementById('liftBanner').innerHTML = `
      Adding your secondary data improved F1 from ${lift.f1_baseline} to ${lift.f1_enriched}
      (+${lift.f1_lift}).
    `;
    document.getElementById('liftBanner').style.display = 'block';
  }

  document.getElementById('modelComparison').style.display = 'block';
}

function renderTierAttribution(attribution) {
  const container = document.getElementById('attributionBars');
  const labels = {
    tier_1: 'Transaction signals',
    tier_2: 'Product/category',
    tier_3: 'Secondary data',
    tier_4: 'Other fields',
  };
  const colors = {
    tier_1: '#3b82f6',
    tier_2: '#10b981',
    tier_3: '#f59e0b',
    tier_4: '#8b5cf6',
  };

  container.innerHTML = `
    <div class="stacked-bar">
      ${Object.entries(attribution).map(([tier, pct]) => `
        <div class="bar-segment" style="width:${pct}%;background:${colors[tier]}"
             title="${labels[tier]}: ${pct}%">
          ${pct > 8 ? `${pct}%` : ''}
        </div>
      `).join('')}
    </div>
    <div class="bar-legend">
      ${Object.entries(attribution).map(([tier, pct]) => `
        <span class="legend-item">
          <span class="legend-dot" style="background:${colors[tier]}"></span>
          ${labels[tier]} (${pct}%)
        </span>
      `).join('')}
    </div>
  `;
}
</script>
```

**F4. Customer List — Multi-source "What Changed"**

```html
<script>
function renderCustomerRow(prediction) {
  const features = prediction.top_features || [];
  const sourceLabels = {
    transaction: 'Transaction',
    'product/category': 'Product',
    secondary_data: 'Secondary',
    other_fields: 'Other',
  };

  return `
    <tr class="risk-${prediction.risk_tier.toLowerCase()}">
      <td>${prediction.customer_id}</td>
      <td>${(prediction.churn_probability * 100).toFixed(0)}%</td>
      <td><span class="risk-badge ${prediction.risk_tier.toLowerCase()}">${prediction.risk_tier}</span></td>
      <td class="what-changed">
        ${features.map(f => `
          <span class="feature-tag tier-${f.tier}">
            <span class="source-label">${sourceLabels[f.source] || ''}</span>
            ${formatFeatureName(f.feature)}
          </span>
        `).join(' ')}
      </td>
      <td class="action-cell">${prediction.action || ''}</td>
    </tr>
  `;
}
</script>
```

---

## LLD: WebSocket Progress Updates

The agent loop broadcasts progress at each step. New message types:

```javascript
// New WebSocket message types
const WS_TYPES = {
  // Existing
  agent_progress: 'agent_progress',
  iteration_result: 'iteration_result',
  champion_selected: 'champion_selected',

  // New
  field_analysis_progress: 'field_analysis_progress',  // "Analyzing field 15/30..."
  churn_window_result: 'churn_window_result',          // "60 days selected (F1=0.78)"
  findings_ready: 'findings_ready',                     // Findings computed, show to user
  pruning_complete: 'pruning_complete',                 // "80 → 52 features after pruning"
  leakage_detected: 'leakage_detected',                // "Removed 3 suspect features"
  model_comparison_ready: 'model_comparison_ready',     // Multi-model results
};
```

---

## Implementation Sequence

### Phase 1: Foundation (Stages 1-2 changes, no model changes)

| Step | Files | What |
|------|-------|------|
| 1.1 | `schemas.py` | Add FileMetadata, extended roles, FindingsResponse |
| 1.2 | `s1_upload.py` | Accept file_type per file |
| 1.3 | `db/models.py` | Add file_type, connection_description to session_files |
| 1.4 | `s2_column_map.py` | Type-aware prompt, extended roles |
| 1.5 | `main.py` | Update multi-upload endpoint |
| 1.6 | `static/index.html` | Per-file radio selector UI |
| 1.7 | Tests | Unit tests for new upload/mapping paths |

### Phase 2: Exhaustive Analysis Engine (Stage 3 rewrite)

| Step | Files | What |
|------|-------|------|
| 2.1 | `s3_field_analysis.py` (NEW) | analyze_numeric, analyze_categorical, analyze_datetime |
| 2.2 | `s3_churn_window.py` (NEW) | Auto churn window with 6 candidates |
| 2.3 | `s3_hypothesis.py` | Rewrite handle() to use field analysis + findings |
| 2.4 | `main.py` | Add findings/confirm and findings/correct endpoints |
| 2.5 | `static/index.html` | Findings screen UI |
| 2.6 | Tests | Unit tests for field analysis (numeric, categorical, datetime) |

### Phase 3: Pruning + Leakage Detection (Stage 4 rewrite)

| Step | Files | What |
|------|-------|------|
| 3.1 | `s4_pruning.py` (NEW) | statistical_pruning, leakage_detection |
| 3.2 | `s4_cross_source.py` (NEW) | Cross-file features, interaction features |
| 3.3 | `s4_features.py` | Rewrite to use pre-computed matrix + pruning |
| 3.4 | Tests | Leakage detection tests (recency, frequency, ablation) |

### Phase 4: Multi-Model Training (Stage 6 rewrite)

| Step | Files | What |
|------|-------|------|
| 4.1 | `s6_train.py` | Multi-model training (A/B/C/D/E) |
| 4.2 | `s5_labels.py` | Compound labels, auto-window integration |
| 4.3 | `agent/loop.py` | Integrate exhaustive analysis, multi-model |
| 4.4 | Tests | Multi-model training tests |

### Phase 5: Results + Inference (Stages 7-8 changes)

| Step | Files | What |
|------|-------|------|
| 5.1 | `s7_results.py` | Multi-model comparison, tier attribution, lift |
| 5.2 | `s8_inference.py` | Multi-source SHAP, action recommendations |
| 5.3 | `static/index.html` | Model comparison table, tier attribution bars, multi-source customer list |
| 5.4 | Tests | Results/inference with multi-model data |

### Phase 6: Agent Loop Integration

| Step | Files | What |
|------|-------|------|
| 6.1 | `agent/loop.py` | Full rewrite with new flow |
| 6.2 | `agent/evaluator.py` | Remove name-based leakage check, use s4_pruning |
| 6.3 | `chat/handler.py` | Handle new message types |
| 6.4 | Integration tests | Full pipeline test with multi-file upload |

### Phase 7: Tier 3 Feature Catalogs (per data type)

| Step | Files | What |
|------|-------|------|
| 7.1 | `features/tier3_loyalty.py` (NEW) | 18 loyalty features |
| 7.2 | `features/tier3_field.py` (NEW) | 16 field features |
| 7.3 | `features/tier3_service.py` (NEW) | 15 service features |
| 7.4 | `features/tier3_returns.py` (NEW) | 15 returns features |
| 7.5 | `features/tier3_master.py` (NEW) | 6 master data features |
| 7.6 | Tests | Per-type feature computation tests |
