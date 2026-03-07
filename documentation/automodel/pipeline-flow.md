# Churn Prediction Pipeline — How It Works

## Overview

The pipeline takes a CSV file of customer transactions and produces a churn prediction model. It runs in two modes:

1. **Sequential mode** — User triggers each stage manually via API buttons
2. **Agent mode** — An automated loop runs stages 4-6 repeatedly, adjusting features between iterations

The frontend is a single HTML page. The backend is FastAPI. LLM calls go to Groq or Gemini.

---

## Persistence

All session data is persisted to PostgreSQL. DataFrames and models are stored as compressed pickle blobs (BYTEA). The in-memory dict in `SessionStore` acts as a cache. Writes go to both cache and DB. Reads check cache first, fall back to DB.

See [database-schema.md](database-schema.md) for table structure.

---

## Stage 1: Upload

**Endpoint:** `POST /api/sessions`

**What happens:**
1. User uploads a CSV file (max 50MB, 500k rows, 50 columns)
2. The system reads it into a pandas DataFrame
3. For each column, the system infers a dtype:
   - Checks if numeric (all values parseable as numbers)
   - Checks if datetime (`pd.to_datetime(format="mixed")`)
   - Checks if categorical (unique count < 50 AND cardinality ratio < 0.05)
   - Otherwise: text
4. Builds a profile: column names, dtypes, null counts, unique counts, 5 sample values per column, date range if datetime columns exist
5. Creates a session in the DB (persisted, no TTL)

**Stored in session:** `dataframe` (raw DataFrame), `profile` (column metadata)

**Returns to frontend:** `session_id`, `profile`

**User Comment** Need to be able to take multiple files. Atleast one file is compulsory. Need text input so that user can describe what is there in each file, and how these two connect. Only upload once user has entered some text, so submit button placement is crucial. 

---

## Stage 2: Column Mapping

**Endpoint:** `POST /api/sessions/{id}/column-mapping`

**What happens:**
1. The system sends the profile to the LLM with this instruction: "Assign a semantic role to each column"
2. The LLM maps each column name to one of these roles:
   - `customer_id` — unique identifier for the customer
   - `transaction_date` — when the transaction happened
   - `amount` — monetary value
   - `product` — what was purchased
   - `quantity` — how many units
   - `category` — product category
   - `channel` — purchase channel (online, store, etc.)
   - `region` — geographic location
   - `other` — not relevant to churn
3. Each mapping has a confidence score (0-1)

**LLM receives:** column name, dtype, null count, unique count, 5 sample values, total row count

**LLM returns:** list of `{name, role, confidence}` for each column

**Stored in session:** `column_mapping` (the role assignments)

**User can override:** `PUT /api/sessions/{id}/column-mapping` with manual corrections

**User Comment** Should run automatically on upload of excel and , and have to visually indicate to the user that this process in ongoing (loader or something). Need to provide user a chance to review, and make corrections. Should also have a summary: explaning what the findings are, and how the multiple files connect with each other and what is there in each file. User should be able to input feedback, then stage 2 should re run, and provide upodate. User should be ok with next step.

---

## Stage 3: Hypothesis

**Endpoint:** `POST /api/sessions/{id}/hypothesis`

**What happens:**
1. The system sends column mappings + sample data to the LLM
2. The LLM returns:
   - **Business type hypothesis** — e.g., "E-commerce retail" with confidence and reasoning
   - **4-8 multiple-choice questions** — to configure the churn model
3. Questions are about: purchase cycle length, churn definition (30/60/90/120 days), business model type (subscription/one-time/repeat), seasonal patterns, domain signals

**LLM receives:** column roles, row count, date range, 3 sample rows

**LLM returns:** `{business_type, confidence, reasoning, questions[]}`

**Stored in session:** `hypothesis`

**The questions serve two purposes:**
- They determine the churn window (how many days of inactivity = churned)
- They inform which features are relevant

**User Comment** Use the best reasoning LLM here that is available within the API provider. Allow user to input free text field as well, to take more inputs. 
---

## Stage 4: Feature Engineering

**Endpoint:** `POST /api/sessions/{id}/features` (body: `{answers: {question_id: value}}`)

**What happens:**

### Step 4a: Determine the churn window
1. Search MCQ answers for a question about churn/inactivity
2. If found and the value is 7-365 days, use it
3. Otherwise, auto-derive: for each customer, compute the median inter-purchase gap, then `churn_window = median_gap * 2` (clamped to 14-365 days)
4. Default fallback: 90 days

### Step 4b: Split the data by time
- `cutoff_date = max_date - churn_window_days`
- `observation_window = transactions where date <= cutoff_date`
- Features are computed only from the observation window

### Step 4c: Compute Tier 1 features (always computed)
These 10 features are always generated for each customer:

| # | Feature | What it measures |
|---|---------|-----------------|
| 1 | `recency` | Days since last purchase (from max observation date) |
| 2 | `frequency_30d` | Number of purchases in last 30 days of observation |
| 3 | `frequency_60d` | Number of purchases in last 60 days |
| 4 | `frequency_90d` | Number of purchases in last 90 days |
| 5 | `monetary_total` | Total amount spent |
| 6 | `monetary_avg` | Average amount per transaction |
| 7 | `frequency_trend` | Frequency in 2nd half minus 1st half of observation |
| 8 | `monetary_trend` | Average amount in 2nd half minus 1st half |
| 9 | `days_between_purchases_avg` | Mean gap (days) between consecutive purchases |
| 10 | `days_between_purchases_std` | Std deviation of purchase gaps |

### Step 4d: Compute Tier 2 features (conditionally computed)
Available only if the required columns exist:

| Feature | Required role | What it measures |
|---------|--------------|-----------------|
| `basket_diversity` | product or category | Unique products/categories per customer |
| `category_concentration` | category | % of purchases in the top category |
| `channel_diversity` | channel | Unique channels per customer |
| `avg_basket_size` | quantity | Mean quantity per transaction |
| `peak_vs_offpeak_ratio` | transaction_date | Purchases in Nov/Dec/Jan vs other months |
| `order_size_trend` | amount | Amount trend (2nd half - 1st half) |
| `product_mix_change` | product | Jaccard distance of products between halves |
| `region_loyalty` | region | % of purchases in the top region |
| `weekend_vs_weekday` | transaction_date | Weekend / weekday purchase ratio |
| `repeat_product_rate` | product | % of products purchased 2+ times |
| `max_gap_between_purchases` | transaction_date | Longest gap between any two purchases |
| `purchase_regularity_score` | transaction_date | max(0, 1 - coefficient_of_variation of gaps) |

The LLM selects which Tier 2 features to compute based on the business hypothesis and MCQ answers.

### Step 4e: Build feature matrix
- Indexed by `customer_id`
- Each column is one feature
- NaN values are retained (filled with 0 during training)

**Stored in session:** `feature_matrix`, `col_map` (role→column_name), `tier1_features`, `tier2_features`, `churn_window_days`, `mcq_answers`

**User Comment** User input on features taken in step 3 should also be calculated here. 

---

## Stage 5: Label Generation

**Endpoint:** `POST /api/sessions/{id}/labels`

**What happens:**
1. Uses the same `cutoff_date = max_date - churn_window_days` from Stage 4
2. Splits the full dataset:
   - `df_before = transactions where date <= cutoff_date` (observation window)
   - `df_after = transactions where date > cutoff_date` (prediction window)
3. Label assignment:
   - Customer appears before cutoff but NOT after → `churn_label = 1` (churned)
   - Customer appears before AND after cutoff → `churn_label = 0` (active)
4. Aligns labels with feature matrix (only customers in both are kept)

**Stored in session:** `labels` (Series indexed by customer_id), `labeled_features` (aligned feature matrix), `cutoff_date`

---

## Stage 6: Model Training

**Endpoint:** `POST /api/sessions/{id}/train`

**What happens:**

### Step 6a: Data preparation
1. Fill NaN with 0
2. Drop columns with zero variance
3. 80/20 stratified train/test split (random_state=42)

### Step 6b: Train XGBoost
```
XGBClassifier(
    n_estimators=100, max_depth=5, learning_rate=0.1,
    scale_pos_weight=(n_negative / n_positive),
    eval_metric="logloss", random_state=42
)
```

### Step 6c: Train Random Forest
```
RandomForestClassifier(
    n_estimators=100, max_depth=8,
    class_weight="balanced", random_state=42
)
```

### Step 6d: Evaluate each model
- AUC: `roc_auc_score(y_test, y_proba)`
- Precision: `precision_score(y_test, y_pred)`
- Recall: `recall_score(y_test, y_pred)`
- F1: `f1_score(y_test, y_pred)`
- Confusion matrix: TP, FP, TN, FN
- Feature importance: from `model.feature_importances_`, sorted descending

### Step 6e: Sort models by AUC descending
`model_results` list is sorted so `model_results[0]` is the one with the highest AUC.

**Stored in session:** `model`, `metrics`, `feature_importance`, `X_test`, `y_test`, `feature_names`


---

## Agent Loop (replaces manual Stages 4-6)

**Endpoint:** `POST /api/sessions/{id}/agent/start`

The agent loop automates feature engineering, training, and evaluation. It runs as a background task with WebSocket progress updates.

### Prerequisites
Stages 1-3 must be completed. The agent needs: `dataframe`, `column_mapping`, `hypothesis`, `mcq_answers`.

### Loop (max 5 iterations)

```
For each iteration:
    1. COMPUTE FEATURES
       - Tier 1 + Tier 2 (same as Stage 4)
       - DSL features (suggested by LLM in previous iterations)
       - Minus excluded features (removed by evaluator or user)

    2. ALIGN with labels
       - Intersection of feature_matrix index and labels index
       - Must have >= 10 samples and >= 2 of each class

    3. TRAIN both models
       - XGBoost + Random Forest (same config as Stage 6)
       - Results sorted by AUC descending

    4. EVALUATE via LLM
       a. Rule-based checks:
          - AUC >= 0.7
          - F1 >= 0.5
          - Top feature importance <= 0.80 (80%)
          - At least 3 features above 5% importance
       b. LLM judgment:
          - Sent: model metrics, feature importance, feature definitions, label definition, iteration history
          - LLM checks for: single feature dominance, perfect metrics, tautological features
          - Returns: leakage_detected, suspect_features, quality_acceptable, best_model, suggested_adjustments
       c. Fallback (if LLM call fails):
          - Uses rule-based checks only
          - best_model = model_results[0].name (highest AUC)
          - quality_acceptable = rule_check.passed

    5. CHECK USER OVERRIDES (from chat)
       - remove_features, add_features, change_criteria, stop, skip_to_completion

    6. SUCCESS CHECK
       - If quality_acceptable AND NOT leakage_detected:
         → Champion = model matching evaluation.best_model
         → Status = "success"
         → Break

    7. ADJUST
       - Remove suspect features (add to excluded list)
       - Ask LLM to suggest 2-5 new DSL features
       - Continue to next iteration

If all 5 iterations complete without success:
    → Pick model with highest AUC across ALL iterations
    → Status = "completed"
```

**User Comment** There are 3 problems you noticed previously:   Three problems:

  1. Same leakage, different name. The agent's feature DSL generated recent_revenue_ratio which is the same signal as recency. The evaluator didn't catch it because it checks feature
  names against the label definition — a ratio feature named differently slips through.
  2. Wrong champion. Previous analysis concluded "Random Forest beats XGBoost in every configuration." Current run confirms this (RF: F1 0.9245, Precision 1.0 vs XGB: F1 0.8991,
  Precision 0.9423). But xgboost was crowned because model_results is sorted by AUC, and the fallback logic picks model_results[0].
  3. Agent didn't iterate on the leakage. The 61.9% dominance is below the 80% hard threshold, and the LLM calls were rate-limited, so the fallback said "rules passed" and accepted
  the model. In the previous manual analysis, you tested with and without recency — the agent should have done the same but didn't.

  The root cause: the evaluator relies on feature name matching for leakage detection, not semantic analysis of what the feature measures. A feature called recent_revenue_ratio isn't
  flagged as tautological with the churn label, even though it measures the same thing as recency.

  The fixes would be:
  - Semantic leakage detection (check feature definitions, not just names)
  - Composite scoring for champion selection (not AUC-only)
  - Lower the single-feature dominance threshold from 80% to something like 50-60%



### WebSocket Messages (server → client)
| Type | When | Data |
|------|------|------|
| `agent_progress` | Each sub-step | iteration, status, detail text |
| `iteration_result` | After evaluation | iteration, model metrics, evaluation, features_used |
| `agent_response` | Feature add/remove | text description |
| `champion_selected` | Final model picked | champion name, metrics, feature importance |

---

## Feature DSL (used by agent loop)

The LLM can suggest features using a structured format. The DSL interpreter converts them to pandas operations.

| Operation | What it computes |
|-----------|-----------------|
| `aggregate` | Per-customer aggregation (sum, mean, count, etc.) |
| `aggregate_window` | Aggregation within last N days |
| `ratio` | Ratio of two aggregations (e.g., recent revenue / total revenue) |
| `trend` | 2nd half value minus 1st half value |
| `conditional_count` | Count of transactions matching a condition (e.g., amount > 50) |
| `nunique` | Distinct count per customer |
| `gap_stat` | Statistic on inter-purchase gaps (max, min, mean, std, median) |

DSL features are appended to the feature matrix alongside Tier 1 and Tier 2 features.

---

## Chat Interface

**Endpoint:** `WS /api/sessions/{id}/chat?token=<jwt>`

The user can send messages while the agent loop runs. The LLM classifies each message as:

| Intent | What happens |
|--------|-------------|
| `command` | Modifies agent state (remove feature, add feature, change criteria, stop, force model, skip to completion) |
| `question` | LLM answers from pipeline context (features, metrics, reasoning) |
| `approval` | User accepts the champion model |

Commands are applied as `user_overrides` on the `AgentState`. The agent loop checks for overrides between evaluation and success check.

---

## LLM Calls Summary

| Stage | Call | Input | Output Schema |
|-------|------|-------|--------------|
| 2 | Column mapping | column profiles | `LLMColumnMappingOutput` |
| 3 | Hypothesis + MCQs | column roles + samples | `LLMHypothesisOutput` |
| 4 | Tier 2 selection | business type + MCQ answers + available features | `LLMFeatureSelectionOutput` |
| Agent | Model evaluation | model metrics + feature importance + label info + history | `LLMEvaluationOutput` |
| Agent | Feature suggestion | data profile + col_map + hypothesis + existing features + metrics | `LLMFeatureSuggestionOutput` |
| Chat | Message handling | user text + pipeline state summary | `LLMChatOutput` |

All LLM calls use structured output (JSON mode with Pydantic schema). Retry logic: 3 attempts with 15s/30s/45s backoff on rate limit errors.

---

## Known Issues

### 1. Wrong champion selection
**Problem:** `model_results` is sorted by AUC descending. The fallback evaluator (when LLM fails) picks `model_results[0]` as best. This means XGBoost wins whenever its AUC is marginally higher, even if Random Forest has a better F1 and Precision.

**Evidence:** Previous testing showed Random Forest beats XGBoost on this dataset in every configuration. Current run selected XGBoost despite RF having F1 0.9245 vs 0.8991, Precision 1.0 vs 0.9423.

**Root cause:** Champion selection uses AUC as the sole metric. No composite scoring.

### 2. Recency leakage not caught
**Problem:** The `recency` feature (days since last purchase) is tautological with the churn label (no purchase in N days). The agent's DSL can generate `recent_revenue_ratio` which is the same signal under a different name.

**Evidence:** `recency` at 61.1% importance (previous run), `recent_revenue_ratio` at 61.9% (current run). Same pattern, different name.

**Root cause:**
- The evaluator checks feature *names*, not *definitions*, for tautological overlap
- Feature definitions passed to the LLM are `{feature_name: feature_name}` (line 304: `feature_defs = {f: f for f in all_features}`), so the LLM has no information about what each feature actually measures
- The 80% dominance threshold is too high. A feature at 61% importance that is tautological with the label should be flagged

### 3. WebSocket race condition
**Problem:** The agent starts as a background task, then the frontend connects WebSocket. By the time the WebSocket is established, iteration 1's broadcast messages have already fired.

**Evidence:** Comparison table shows only iteration 2 results. Iteration 1 was missed.

**Root cause:** In the frontend, `fetch('/agent/start')` fires first, then `connectWebSocket()` runs after. The agent loop starts immediately in the background and broadcasts before the WebSocket connection is open.

### 4. Start Agent button not disabled
**Problem:** Clicking "Start Agent" multiple times shows raw JSON error messages: `{"detail":"Agent already running"}`.

**Root cause:** The button is not disabled after the first click. The error message is not parsed from JSON before display.

### 5. Feature definitions not passed to evaluator
**Problem:** Line 304 of `loop.py` builds feature definitions as `{f: f for f in all_features}` — mapping each feature name to itself. The LLM evaluator receives no information about what `recency` or `recent_revenue_ratio` actually measures.

**Impact:** The LLM cannot perform semantic leakage detection. It cannot determine that `recent_revenue_ratio` (recent revenue / total revenue) is a proxy for recency, which overlaps with the churn label definition.
