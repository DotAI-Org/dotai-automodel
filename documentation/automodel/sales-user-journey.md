# Sales User Journey — Churn Prediction Tool

## Who is this for

A sales person who has customer transaction data in CSV files. They want one thing: a list of customers who are about to stop buying, so they can act on it. They do not know what AUC, F1, XGBoost, or feature engineering means. They should not have to.

---

## What the user cares about

1. Which customers should I call this week?
2. Why is this customer at risk?
3. How much can I trust these predictions?

What the user does NOT care about:
- Column dtypes, confidence scores, model comparison metrics
- Model names (XGBoost vs Random Forest)
- Iteration counts, feature DSL, tier classifications
- Pipeline internals

---

## Journey Overview

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐
│  Login   │ ──> │ Upload Data  │ ──> │ Your Business│
└─────────┘     └──────────────┘     └──────────────┘
                                            │
                                            v
                                     ┌──────────────┐
                                     │  Predictions  │
                                     └──────────────┘
```

3 steps from the user's perspective. 7 pipeline stages run behind the scenes.

| User sees | Pipeline stages running |
|-----------|----------------------|
| Upload Data | Stage 1 (upload) + Stage 2 (column mapping) |
| Your Business | Stage 3 (hypothesis) + MCQ |
| Predictions | Stage 4 (features) + Stage 5 (labels) + Stage 6 (training) + Agent loop |

---

## Screen 1: Login

**Headline:** Predict which customers will leave

**Subtext:** Upload your transaction history. Get a risk score for every customer.

**Action:** Sign in with Google (same OAuth flow as current)

**No changes to auth backend.** Same JWT, same Google SSO.

---

## Screen 2: Upload Your Data

### 2a: File Selection

**Headline:** Upload your transaction data

**Guidance box** (always visible, above the drop zone):

```
┌──────────────────────────────────────────────────┐
│  Your file should have:                          │
│                                                  │
│  • Customer ID — who made the purchase           │
│  • Date — when it happened                       │
│  • Amount — how much they spent                  │
│                                                  │
│  Optional: Product, Category, Region, Channel    │
│                                                  │
│  CSV format. One row per transaction.            │
│  ↓ Download sample file                          │
└──────────────────────────────────────────────────┘
```

**Drop zone:** Same drag/drop as current.

**Description field:** "What does this data represent?" — same as current. Required before upload.

**Upload button:** "Upload & Analyze"

### 2b: Data Summary (replaces Column Mapping Review)

After upload + column mapping complete, show:

```
┌──────────────────────────────────────────────────┐
│  Your data at a glance                           │
│                                                  │
│  Customers:     1,247                            │
│  Transactions:  34,892                           │
│  Date range:    Jan 2024 — Dec 2024              │
│                                                  │
│  We identified these columns:                    │
│                                                  │
│  ✓ Customer ID     ← "cust_id"                  │
│  ✓ Purchase Date   ← "order_date"               │
│  ✓ Amount          ← "total_amount"              │
│  ✓ Product         ← "item_name"                 │
│  ✓ Region          ← "city"                      │
│                                                  │
│  [Something wrong? Edit]        [Looks good →]   │
└──────────────────────────────────────────────────┘
```

**Key differences from current:**
- Shows data summary (customer count, transaction count, date range) — gives confidence the file was read correctly
- Column roles shown as friendly labels ("Customer ID" not "customer_id role")
- No dtype column
- No confidence percentage
- "Edit" expands the full mapping table with dropdowns (same as current review panel) + feedback textarea
- "Looks good" proceeds to Screen 3

**Behind the scenes:** Upload (Stage 1) runs on button click. Column mapping (Stage 2) runs automatically after upload. The spinner shows "Analyzing your file..." during this.

---

## Screen 3: Tell Us About Your Business

**Headline:** Help us understand your business

**Subtext:** Your answers help us focus on the patterns that matter for your customers.

### Layout

```
┌──────────────────────────────────────────────────┐
│  Anything we should know about your customers?   │
│  (optional)                                      │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │ e.g. "Customers who buy only during      │    │
│  │ festivals tend to leave after the season" │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  ─────────────────────────────────────────────   │
│                                                  │
│  How often do your customers purchase?           │
│  ○ Weekly    ○ Monthly    ○ Quarterly            │
│                                                  │
│  After how many days without a purchase would    │
│  you consider a customer "lost"?                 │
│  ○ 30 days   ○ 60 days   ○ 90 days   ○ 120 days │
│                                                  │
│  What type of business is this?                  │
│  ○ Subscription   ○ One-time purchase            │
│  ○ Repeat purchase  ○ Other                      │
│                                                  │
│  ... (more MCQ questions from LLM)               │
│                                                  │
│  [← Back]                   [Build Predictions]  │
└──────────────────────────────────────────────────┘
```

**Flow:**
1. On entering this screen, hypothesis generation (Stage 3) runs with spinner: "Analyzing your business..."
2. When hypothesis returns, MCQ questions appear
3. Free text area is above the questions
4. "Build Predictions" submits MCQ answers (Stage 4 features) and starts the agent loop

**Same backend.** No API changes. The frontend sequences the calls.

---

## Screen 4: Your Predictions

### Phase A: Building

The agent loop runs. The user sees a progress view that explains what is happening and why.

```
┌──────────────────────────────────────────────────┐
│  Building your prediction model...               │
│                                                  │
│  Round 1                                         │
│  ├─ ✓ Prepared 10 customer features              │
│  │    recency, purchase frequency, total spend,  │
│  │    average order value, ...                   │
│  ├─ ✓ Trained prediction models                  │
│  ├─ ✓ Evaluated results                          │
│  └─ ⚠ "Days since last purchase" dominated       │
│       predictions (62%). Removing it and adding  │
│       new features to get a more balanced model. │
│                                                  │
│  Round 2                                         │
│  ├─ ✓ Added 3 new features:                      │
│  │    purchase frequency trend, product variety   │
│  │    change, weekend shopping ratio             │
│  ├─ ⟳ Training models...                         │
│  │                                               │
│  This can take 1-3 minutes.                      │
│                                                  │
│  ┌─ Chat ──────────────────────────────────┐     │
│  │ ▸ Have a question? Ask here...          │     │
│  └─────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

**How iteration progress maps to agent loop messages:**

| Agent event | What the user sees |
|-------------|-------------------|
| `agent_progress`: computing features | "Prepared N customer features" + feature name list |
| `agent_progress`: training | "Training prediction models..." |
| `iteration_result` | "Evaluated results" |
| Evaluation: leakage detected | "Feature X dominated predictions (Y%). Removing it..." |
| Evaluation: quality not acceptable | "Model accuracy too low. Adjusting features..." |
| New features suggested | "Added N new features: [plain names]" |
| Evaluation: quality acceptable | Transition to Phase B (results) |

**Round numbering:** Each agent iteration = one "Round". Shows what happened in each round: what features were used, what the result was, what adjustment was made.

**Chat panel:** Visible at the bottom, collapsed to one line. Click to expand. User can type questions ("what does purchase frequency trend mean?") or commands ("remove the region feature"). Same WebSocket, same backend.

### Phase B: Results

```
┌──────────────────────────────────────────────────┐
│                                                  │
│              Predictions Ready                   │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │                                            │  │
│  │    85 out of 100                           │  │
│  │    at-risk customers identified            │  │
│  │                                            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  What drives customers to leave:                 │
│                                                  │
│  1. Purchase frequency declining  ████████  34%  │
│  2. Fewer products per order      ██████    22%  │
│  3. Longer gaps between orders    █████     18%  │
│  4. Stopped buying top category   ███       12%  │
│  5. Switched from weekday buys    ██         8%  │
│                                                  │
│  ┌──────────────────────────────────────┐        │
│  │       ↓ Download Predictions         │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  ▸ View model details                            │
│                                                  │
│  ┌─ Chat ──────────────────────────────────┐     │
│  │ ▸ Have a question? Ask here...          │     │
│  └─────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

**Headline metric:** "85 out of 100 at-risk customers identified" = recall score stated in business terms. If recall is 0.85, this becomes "85 out of 100".

**Feature importance:** LLM translates raw feature names to plain language. One LLM call after champion selection. Mapping:

| Raw feature name | Plain language |
|-----------------|---------------|
| `frequency_trend` | Purchase frequency declining |
| `basket_diversity` | Fewer products per order |
| `days_between_purchases_avg` | Longer gaps between orders |
| `category_concentration` | Stopped buying top category |
| `weekend_vs_weekday` | Switched from weekday to weekend buys |
| `recency` | No recent purchases |
| `monetary_trend` | Spending less over time |

**Download Predictions** — primary action button. Downloads a CSV.

**"View model details"** — expands a section with:
- Model name (XGBoost / Random Forest)
- AUC, F1, Precision, Recall
- Full comparison table across iterations
- Training rounds summary

---

## Downloaded Predictions CSV

The output file the user gets:

| Customer ID | Risk Score | Risk Level | Top Risk Factor |
|-------------|-----------|------------|-----------------|
| C-1234 | 0.92 | High | No purchases in 45 days |
| C-5678 | 0.71 | Medium | Order frequency dropped 40% |
| C-9012 | 0.45 | Medium | Switched to fewer products |
| C-3456 | 0.23 | Low | — |

**Columns:**
- `Customer ID` — from the customer_id column in their data
- `Risk Score` — model probability (0-1), rounded to 2 decimals
- `Risk Level` — High (>0.7), Medium (0.4-0.7), Low (<0.4)
- `Top Risk Factor` — plain language explanation of the top contributing feature for that customer. Requires per-customer SHAP or feature contribution (existing in pipeline via `shap` library).

Sorted by Risk Score descending — highest risk first.

---

## Sidebar

Same sidebar as current. Status label changes:

| Current status | New label |
|---------------|-----------|
| upload | Data uploaded |
| mapping | Reviewing data |
| hypothesis | Setting up |
| features | Setting up |
| agent | Building model |
| results | Predictions ready |

---

## Error States

| Error | What the user sees |
|-------|-------------------|
| CSV has no customer ID column | "We couldn't find a customer ID column. Your file needs a column that identifies each customer." |
| CSV has no date column | "We couldn't find a date column. Your file needs a column with purchase dates." |
| Too few customers (<30) | "Your file has X customers. We need at least 30 customers to build predictions." |
| Too few transactions (<100) | "Your file has X transactions. We need at least 100 transactions to build predictions." |
| Model training fails | "Something went wrong while building the model. Try uploading a different file, or ask in the chat for help." |
| Agent timeout | "Model building is taking longer than expected. Your session is saved — come back later." |

---

## Backend Changes Required

| Change | File | Description |
|--------|------|-------------|
| Feature name translation | `app/agent/loop.py` or new endpoint | LLM call to translate raw feature names to plain language after champion selection |
| Per-customer risk factor | `app/stages/s8_inference.py` | Use SHAP values or feature contributions to pick the top factor per customer |
| Risk level column | `app/stages/s8_inference.py` | Map probability to High/Medium/Low |
| Data summary in profile | `app/stages/s1_upload.py` | Return customer count, transaction count, date range in profile response |
| Iteration context in WS messages | `app/agent/loop.py` | Include feature names, removal reasons in `agent_progress` messages |

**No new API endpoints needed.** All changes are to existing responses and the frontend.

---

## What stays the same

- Auth flow (Google SSO, JWT)
- All API endpoints and their contracts
- Session persistence (PostgreSQL)
- Agent loop logic (iterations, evaluation, feature suggestion)
- Chat WebSocket protocol
- Sidebar session management (list, rename, delete)

---

## Implementation approach

Single-pass rewrite of `static/index.html`. The backend API responses already contain the data needed — the frontend will reformat it for the user. The 5 backend changes listed above add fields to existing responses; they do not change API contracts.
