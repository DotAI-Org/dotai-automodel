# AutoModel: Self-Service Churn Prediction Backend

## Overview

Standalone FastAPI application. Users upload a transaction CSV. The system profiles the data, uses Gemini to understand the business context, builds an XGBoost churn model, and delivers per-user predictions with SHAP explanations.

No prior knowledge of the user's business is required. The LLM handles understanding; classical ML handles prediction.

---

## Project Location

```
churn-tool/
├── app/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── session_store.py      # In-memory session dict with 24h TTL
│   ├── models/
│   │   └── schemas.py        # Pydantic models for all request/response shapes
│   ├── stages/
│   │   ├── s1_upload.py      # CSV parsing & data profiling
│   │   ├── s2_column_map.py  # LLM column understanding
│   │   ├── s3_hypothesis.py  # LLM business hypothesis + MCQ generation
│   │   ├── s4_features.py    # LLM feature selection + feature computation
│   │   ├── s5_labels.py      # Churn label generation
│   │   ├── s6_train.py       # XGBoost training & evaluation
│   │   ├── s7_results.py     # LLM results summary
│   │   └── s8_inference.py   # Model inference + SHAP + CSV download
│   └── llm/
│       └── client.py         # Gemini API wrapper with structured output
├── requirements.txt
├── Dockerfile
└── tests/
    ├── test_data/            # Sample CSVs
    ├── generate_test_data.py # Script to create test CSV
    └── test_pipeline.py      # End-to-end pipeline test
```

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Web framework | FastAPI |
| CSV parsing | pandas |
| LLM | Google Gemini (`google-genai`) |
| ML | XGBoost |
| Train/eval | scikit-learn |
| Feature explanations | SHAP |
| Structured LLM output | Pydantic + Gemini JSON mode |

---

## Pipeline: 8 Stages

```
Stage 1 → 2 → 3 → 4 → 5 → 6 → 7
                                 ↓
                          Accept? → Yes → Stage 8
                                 ↓ No
                          Loop back to 4 or 5
```

### Stage 1: CSV Upload & Profiling

**Endpoint:** `POST /sessions`
**Input:** Multipart file upload (CSV)
**LLM:** No

Parses the CSV with pandas. Builds a data profile containing:
- Column names, inferred dtypes (numeric, categorical, datetime, text)
- Null count, unique count per column
- 5 sample rows
- Row count, date range (if datetime columns detected)

Creates a session ID and stores the profile in memory.

**Response shape:**
```json
{
  "session_id": "string",
  "profile": {
    "columns": [{ "name", "dtype", "null_count", "unique_count", "sample_values" }],
    "row_count": 5000,
    "sample_rows": [{...}],
    "date_range": { "column", "min", "max" }
  }
}
```

**Constraints:**
- Max file size: 50MB
- Max rows: 500,000
- Max columns: 50

---

### Stage 2: LLM Column Mapping

**Endpoint:** `POST /sessions/{id}/column-mapping`
**Input:** None (reads profile from session)
**LLM:** Yes (Gemini structured output)

Sends the data profile to Gemini. The LLM assigns a semantic role to each column from a fixed enum:

`customer_id`, `transaction_date`, `amount`, `product`, `quantity`, `category`, `channel`, `region`, `other`

**Override endpoint:** `PUT /sessions/{id}/column-mapping` — user can correct any role assignment.

**Response shape:**
```json
{
  "columns": [{ "name", "dtype", "llm_role", "confidence" }]
}
```

---

### Stage 3: Business Hypothesis & MCQ Generation

**Endpoint:** `POST /sessions/{id}/hypothesis`
**Input:** None (reads column mapping + profile from session)
**LLM:** Yes (Gemini structured output)

The LLM receives the confirmed column mapping, sample data, and stats. Returns:
1. Business type hypothesis (e.g., "E-commerce retail") with confidence and reasoning
2. 4-8 MCQ objects covering purchase cycle, churn threshold, business model, seasonal patterns

MCQs are LLM-generated, not hardcoded.

**Response shape:**
```json
{
  "hypothesis": { "type", "confidence", "reasoning" },
  "questions": [{ "id", "question", "options": [{ "label", "value" }], "context" }]
}
```

---

### Stage 4: Feature Engineering

**Endpoint:** `POST /sessions/{id}/features`
**Input:** `{ "answers": { "question_id": "selected_value" } }`
**LLM:** Yes (feature selection only)

Uses a pre-built feature catalog. No code generation. The LLM selects which Tier 2 features to compute.

#### Tier 1 — Universal (10 features, always computed)

| Feature | Description |
|---------|-------------|
| `recency` | Days since last transaction |
| `frequency_30d` | Transaction count in last 30 days |
| `frequency_60d` | Transaction count in last 60 days |
| `frequency_90d` | Transaction count in last 90 days |
| `monetary_total` | Total spend |
| `monetary_avg` | Average transaction value |
| `frequency_trend` | Purchase frequency change (first half vs second half) |
| `monetary_trend` | Spend change (first half vs second half) |
| `days_between_purchases_avg` | Average inter-purchase interval |
| `days_between_purchases_std` | Variability of inter-purchase interval |

#### Tier 2 — Industry-specific (12 features, LLM selects)

| Feature | Requires Column |
|---------|----------------|
| `basket_diversity` | product |
| `category_concentration` | category |
| `channel_diversity` | channel |
| `avg_basket_size` | quantity |
| `peak_vs_offpeak_ratio` | transaction_date |
| `order_size_trend` | amount |
| `product_mix_change` | product |
| `region_loyalty` | region |
| `weekend_vs_weekday` | transaction_date |
| `repeat_product_rate` | product |
| `max_gap_between_purchases` | transaction_date |
| `purchase_regularity_score` | transaction_date |

Each feature is a pre-built pandas function: `def compute_{feature}(df, column_mapping) -> Series`

Transaction-level CSV is aggregated into a user-level feature matrix.

**Response shape:**
```json
{
  "feature_count": 22,
  "user_count": 200,
  "feature_tiers": { "tier1": [...], "tier2": [...] },
  "stats": [{ "name", "mean", "median", "null_pct" }]
}
```

---

### Stage 5: Churn Label Generation

**Endpoint:** `POST /sessions/{id}/labels`
**Input:** None
**LLM:** No

Churn window determination:
1. From MCQ answer if user provided a value
2. Otherwise auto-derived: 2x median inter-purchase interval
3. Clamped to 14-365 days

Temporal cutoff: `max_date - churn_window`
Label: 1 if no purchase after cutoff, 0 otherwise

**Response shape:**
```json
{
  "churn_rate": 0.46,
  "churned_count": 92,
  "active_count": 108,
  "churn_window_days": 37,
  "cutoff_date": "2024-11-24"
}
```

---

### Stage 6: Model Training

**Endpoint:** `POST /sessions/{id}/train`
**Input:** None
**LLM:** No

- Algorithm: XGBoost (binary classification)
- 80/20 stratified split
- Class imbalance handling via `scale_pos_weight`
- Metrics: AUC-ROC, precision, recall, F1
- Confusion matrix
- Feature importance (top 10)

**Response shape:**
```json
{
  "metrics": { "auc", "precision", "recall", "f1" },
  "confusion_matrix": { "true_positive", "false_positive", "true_negative", "false_negative" },
  "feature_importance": [{ "feature", "importance" }],
  "training_time_seconds": 0.5
}
```

---

### Stage 7: Results Presentation

**Endpoint:** `GET /sessions/{id}/results`
**Input:** None
**LLM:** Yes (summary generation)

Combines Stage 6 metrics with a plain-language LLM summary. Includes 10-20 sample predictions from the test set.

**Response shape:**
```json
{
  "summary": "LLM-generated business language summary",
  "metrics": { "auc", "precision", "recall", "f1" },
  "feature_importance": [{ "feature", "importance" }],
  "sample_predictions": [{ "customer_id", "churn_probability", "risk_tier", "actual_churned" }]
}
```

---

### Stage 8: Inference

**Endpoint:** `POST /sessions/{id}/inference`
**Input:** None
**LLM:** No

Runs the trained model on all users in the feature matrix. Per user:
- Churn probability
- Risk tier: High (>0.7), Medium (0.4-0.7), Low (<0.4)
- Top 3 feature contributions via SHAP values

**Response shape:**
```json
{
  "total_users": 200,
  "high_risk_count": 60,
  "medium_risk_count": 40,
  "low_risk_count": 100,
  "predictions": [{ "customer_id", "churn_probability", "risk_tier", "top_features": [{ "feature", "contribution" }] }]
}
```

**CSV Download:** `GET /sessions/{id}/inference/download`
Returns a CSV file with columns: `customer_id`, `churn_probability`, `risk_tier`, `top_feature_contributions`

---

## Session Management

Sessions are stored in-memory as a Python dict:

```
sessions[session_id] = {
    created_at, stage, profile, column_mapping, hypothesis,
    mcq_answers, feature_matrix, col_map, labels, labeled_features,
    model, metrics, predictions, ...
}
```

- TTL: 24 hours
- Background thread cleans up expired sessions every hour
- Session object grows as the user progresses through stages
- No persistence in v1

---

## LLM Integration

All LLM calls use Gemini structured output (JSON mode) with a Pydantic schema defining the response shape. This avoids parsing issues.

**LLM calls occur in 4 stages:**

| Stage | Purpose | Schema |
|-------|---------|--------|
| 2 | Column role mapping | `LLMColumnMappingOutput` |
| 3 | Business hypothesis + MCQ generation | `LLMHypothesisOutput` |
| 4 | Tier 2 feature selection | `LLMFeatureSelectionOutput` |
| 7 | Results summary | `LLMResultsSummaryOutput` |

**Configuration:**
- Model: `gemini-2.0-flash`
- Temperature: 0.2
- Requires `GEMINI_API_KEY` environment variable

---

## Running Locally

```bash
cd churn-tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
GEMINI_API_KEY=your_key uvicorn app.main:app --port 8001
```

Requires `libomp` on macOS for XGBoost: `brew install libomp`

---

## Running with Docker

```bash
cd churn-tool
docker build -t churn-tool .
docker run -p 8001:8000 -e GEMINI_API_KEY=your_key churn-tool
```

---

## Testing

### Generate test data

```bash
cd churn-tool
python tests/generate_test_data.py
```

Creates `tests/test_data/ecommerce_sample.csv` — 5000 transactions, 200 customers, 30% churn signal.

### Run end-to-end test

```bash
GEMINI_API_KEY=your_key python tests/test_pipeline.py
```

### Manual verification via curl

```bash
# Stage 1
curl -F "file=@tests/test_data/ecommerce_sample.csv" http://localhost:8001/sessions

# Stage 2
curl -X POST http://localhost:8001/sessions/{id}/column-mapping

# Stage 3
curl -X POST http://localhost:8001/sessions/{id}/hypothesis

# Stage 4
curl -X POST http://localhost:8001/sessions/{id}/features \
  -H "Content-Type: application/json" \
  -d '{"answers": {"q_purchase_cycle": "monthly"}}'

# Stage 5
curl -X POST http://localhost:8001/sessions/{id}/labels

# Stage 6
curl -X POST http://localhost:8001/sessions/{id}/train

# Stage 7
curl http://localhost:8001/sessions/{id}/results

# Stage 8
curl -X POST http://localhost:8001/sessions/{id}/inference
curl http://localhost:8001/sessions/{id}/inference/download -o predictions.csv
```

---

## Iteration Loop

If model AUC < 0.65 or user rejects results:

1. System suggests adding more features, adjusting churn window, or reviewing column mapping
2. User loops back to Stage 4 or 5
3. Re-trains with updated configuration
4. Max 3 iterations before suggesting the data may lack sufficient signal

---

## Data Size Constraints (v1)

| Constraint | Limit |
|------------|-------|
| Max CSV size | 50MB |
| Max rows | 500,000 |
| Max columns | 50 |

---

## API Endpoint Summary

| Method | Path | Stage | LLM |
|--------|------|-------|-----|
| POST | `/sessions` | 1 | No |
| POST | `/sessions/{id}/column-mapping` | 2 | Yes |
| PUT | `/sessions/{id}/column-mapping` | 2 | No |
| POST | `/sessions/{id}/hypothesis` | 3 | Yes |
| POST | `/sessions/{id}/features` | 4 | Yes |
| POST | `/sessions/{id}/labels` | 5 | No |
| POST | `/sessions/{id}/train` | 6 | No |
| GET | `/sessions/{id}/results` | 7 | Yes |
| POST | `/sessions/{id}/inference` | 8 | No |
| GET | `/sessions/{id}/inference/download` | 8 | No |
