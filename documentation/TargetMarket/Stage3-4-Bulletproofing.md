# Bulletproofing Stage 3 and Stage 4 for Blind Entry

## The Problem

A Sales VP uploads CSVs. We do not know their vertical, their data type, their purchase cycle, what "churned" means for their business, or which features will predict churn. The current pipeline asks an LLM to guess the business type from column names, generates MCQs the user may answer carelessly, and uses those answers to gate feature selection.

If the guess is wrong, everything downstream is wrong. The model produces a list the VP checks against customers they know — and it misses them. Trust is destroyed in 30 seconds.

This document describes how to make Stage 3 (Hypothesis) and Stage 4 (Feature Engineering) produce results that survive blind entry across 19 verticals and 5 data types.

---

## Core Principle: Compute First, Hypothesize Second

Today: LLM guesses → MCQs → feature selection → model.

Proposed: Exhaustive field analysis → auto-select churn window → LLM hypothesis grounded in facts → user confirms → features already computed → model prunes.

The LLM should never guess what it can compute.

---

## The Exhaustive Field Analysis

After Stage 2, every field has a dtype (numeric, categorical, datetime, text) and a semantic role. Instead of selecting specific statistics for specific fields, run a fixed set of 4 analyses on EVERY field based on its dtype. One computation pass produces both the data signature report (for Stage 3 hypothesis) and the per-customer feature matrix (for Stage 4 training).

### Why Exhaustive

A field mapped as `other` might be `payment_terms` (categorical: "COD", "Net 30", "Net 45"). A selective approach ignores it. The exhaustive approach runs 4 categorical analyses and discovers: customers on "Net 45" churn at 2x the rate of "COD" customers. That signal was in the data. Nobody asked for it.

A numeric field mapped as `other` turns out to be `credit_limit`. The exhaustive approach finds: customers whose per-customer mean credit_limit exceeds a threshold churn at 3x the rate. A selective approach never looked at it because it was not in the pre-defined signature list.

Computing extra fields and dropping them is cheaper than guessing which fields to compute and missing the one that matters.

### The 4 Analyses Per Dtype

#### Every Numeric Field

| # | Analysis | Output (signature) | Output (per-customer feature) |
|---|----------|-------------------|-------------------------------|
| 1 | Distribution | mean, median, std, skew, p25, p75, outlier % (>3 std) | — |
| 2 | Per-customer profile | Group by customer_id → mean, std across customers. How much does this value vary between customers? | `{field}_mean_per_customer`, `{field}_std_per_customer` |
| 3 | Univariate churn signal | Split by churned/active, compare distributions. KS-test p-value + AUC. Does this field separate churners from non-churners? | — (used for pruning, not as a feature) |
| 4 | Temporal trend | If a date field exists, compute slope of this value over time per customer. Rising/falling? | `{field}_trend` (2nd half mean minus 1st half mean per customer) |

**Examples of what this catches:**
- `net_amt` (mapped as `amount`): produces `monetary_avg`, `monetary_trend` — same as current Tier 1, but now computed by the generic engine
- `credit_limit` (mapped as `other`): produces `credit_limit_mean_per_customer` — captures customers whose credit limit is atypically high or low
- `free_quantity` (mapped as `other`): produces `free_quantity_mean_per_customer`, `free_quantity_trend` — captures customers getting fewer freebies over time (a scheme-related churn signal)
- `scheme_discount_pct` (mapped as `other`): produces `scheme_discount_pct_trend` — declining discounts may push dealers away

#### Every Categorical Field

| # | Analysis | Output (signature) | Output (per-customer feature) |
|---|----------|-------------------|-------------------------------|
| 1 | Concentration | Top 5 values + their %, long-tail % | — |
| 2 | Per-customer diversity | Avg unique values per customer | `{field}_diversity` (unique values per customer) |
| 3 | Churn rate by value | For each value, % of customers who churned. Which values correlate with churn? | `{field}_churn_rate` (the churn rate of the customer's most-frequent value) |
| 4 | Temporal shift | Per customer: Jaccard distance of value sets between 1st half and 2nd half | `{field}_shift` (0 = same values, 1 = completely different) |

**Examples of what this catches:**
- `product_group` (mapped as `category`): produces `category_diversity`, `category_shift` — same as current Tier 2 `basket_diversity` and `product_mix_change`, but now generic
- `payment_terms` (mapped as `other`): produces `payment_terms_churn_rate` — captures that "Net 45" customers churn more than "COD" customers
- `zone` (mapped as `region`): produces `zone_diversity`, `zone_shift` — captures customers whose purchasing territory is changing
- `channel_type` (mapped as `other`): produces `channel_type_diversity` — single-channel vs multi-channel customers

#### Every Datetime Field

| # | Analysis | Output (signature) | Output (per-customer feature) |
|---|----------|-------------------|-------------------------------|
| 1 | Recency | Per-customer days since last event (distribution: median, p25, p75) | `{field}_recency` (days since last event for each customer) |
| 2 | Frequency | Per-customer events per month (distribution) | `{field}_frequency_30d`, `{field}_frequency_60d`, `{field}_frequency_90d` |
| 3 | Gap profile | Inter-event gaps per customer: median, std, max, coefficient of variation | `{field}_gap_avg`, `{field}_gap_std`, `{field}_gap_max`, `{field}_gap_cv` |
| 4 | Seasonality | Monthly index: each month's volume / average month | — (signature only, used for hypothesis) |

**Examples of what this catches:**
- `invoice_date` (mapped as `transaction_date`): produces the standard recency/frequency/gap features — same as current Tier 1, but now computed generically
- `last_payment_date` (mapped as `other`): produces `last_payment_date_recency` — captures customers whose payments are becoming less frequent, independent of purchase patterns
- `visit_date` (from field visit file): produces `visit_date_frequency_90d`, `visit_date_gap_avg` — captures visit cadence changes

#### Text Fields

Skip. Text fields are not analyzed. (Cardinality count stored for reference only.)

### Two Outputs From One Pass

The exhaustive analysis produces:

**Output 1: Data Signature Report** — aggregated statistics per field. Fed to the LLM for hypothesis generation in Stage 3c. Also shown to the user in Stage 3d.

**Output 2: Per-Customer Feature Matrix** — one row per customer, one column per computed feature. Fed directly to Stage 4 for training. No separate feature engineering step needed for these features.

A dataset with 30 columns produces roughly:
- Numeric fields (say 12): 12 × 3 features = 36 features
- Categorical fields (say 8): 8 × 3 features = 24 features
- Datetime fields (say 3): 3 × 7 features = 21 features
- Total: ~81 features before pruning

This is manageable. XGBoost handles 80 features without difficulty at 1000+ customers.

### Cross-File Signatures (Multi-File Upload)

In addition to per-field analysis, compute cross-file statistics when multiple files are uploaded:

| Signature | What it reveals |
|-----------|----------------|
| Engagement-purchase correlation | Among customers in both files, Pearson r between loyalty activity and purchase value |
| Service-churn overlap | Among lapsed customers, % with service tickets in last 90d vs active customers |
| Visit-order linkage | % of rep visits followed by a purchase within 7 days |
| Influencer coverage per dealer | Distribution of linked influencers per dealer |
| Data overlap rate | % of transaction customers that appear in the secondary file. If 5%, secondary data covers too little to matter. |

These are computed once, reported in the signature, and also generate cross-source features (see Stage 4 section).

### Implementation

A new module `app/stages/s3_field_analysis.py`:

```python
def analyze_all_fields(df, col_map, labels=None) -> tuple[dict, pd.DataFrame]:
    """
    Run 4 analyses per field based on dtype.

    Args:
        df: raw DataFrame
        col_map: column mapping from Stage 2
        labels: optional churn labels (for univariate signal analysis)

    Returns:
        signature: dict of per-field statistics (for LLM + user display)
        feature_matrix: DataFrame indexed by customer_id (for training)
    """

def analyze_numeric(df, col_name, customer_id_col, date_col=None, labels=None) -> tuple[dict, dict[str, pd.Series]]
def analyze_categorical(df, col_name, customer_id_col, date_col=None, labels=None) -> tuple[dict, dict[str, pd.Series]]
def analyze_datetime(df, col_name, customer_id_col) -> tuple[dict, dict[str, pd.Series]]

def analyze_cross_file(df_txn, df_secondary, col_map, labels=None) -> tuple[dict, pd.DataFrame]
```

Each `analyze_*` function returns a tuple of (signature_dict, features_dict). The parent function concatenates all features into a single DataFrame.

### Compute Cost

For a 30-column dataset with 500K rows:
- 30 fields × 4 analyses each = 120 pandas operations
- Each operation: groupby + aggregation = <0.5s
- Total: 15-30 seconds
- Acceptable within the 5-minute target

---

## Stage 3: Revised Flow

### 3a. Exhaustive Field Analysis

After column mapping, run `analyze_all_fields()` on each uploaded file. This replaces the previous "compute data signatures" step with a broader, dtype-based approach that covers every field.

The output is:
1. A signature report covering every field (not just the ones we thought to check)
2. A per-customer feature matrix (used later in Stage 4)

### 3b. Auto-Select Churn Window

The churn window determines labels. Wrong window = wrong labels = wrong model.

**Current approach:** MCQ answer, or 2x median gap, or 90-day default.

**Why it fails:**
- 2x median gap works for regular purchasers. Fails for seasonal (agri — 6-month gaps between kharif/rabi), project-based (cement — irregular), mixed-frequency (some weekly, some quarterly).
- The MCQ forces the VP to pick 30/60/90/120 days. They do not think in these terms.
- A single global window treats all customers the same. A weekly buyer and a quarterly buyer have different thresholds.

**Proposed: Test multiple windows, let data decide.**

```
1. Compute candidate windows: 30, 60, 90, 120, 180, 365 days
2. For each window:
   a. Generate labels (churned = no purchase after max_date - window)
   b. Compute churn rate
   c. Discard windows where churn rate < 5% or > 80%
3. For each surviving window:
   a. Use the feature matrix already computed in 3a (no recomputation needed)
   b. Train a fast XGBoost (50 trees, no tuning)
   c. Record F1 on 20% holdout
4. Pick the window with the best F1
5. Store: selected_window, all_window_results, per-customer adaptive gap
```

Note: Step 3a already produced the feature matrix. The churn window test reuses it — only the labels change per window. This means testing 6 windows costs 6 × (label generation + fast XGBoost) ≈ 5-10 seconds, not 6 × (features + labels + XGBoost).

**Per-customer adaptive gap (computed as a feature, not as a label):**
- For each customer, compute their personal median inter-purchase gap
- Feature: `gap_vs_personal_median` = current_gap / personal_median_gap
- A value of 2.5 means the customer has been silent for 2.5x their normal interval
- This handles mixed-frequency customer bases without a global window

### 3c. LLM Hypothesis (Grounded in Computed Facts)

The LLM prompt changes from:

> "Here are column names and sample values. What business is this?"

To:

> "Here is the complete field analysis of a dataset:
>
> NUMERIC FIELDS:
> - net_amt: mean=12,450, median=8,200, skew=2.1, per-customer std=15,400. Univariate churn AUC=0.58.
> - free_quantity: mean=2.3, median=0, skew=4.8, per-customer std=5.1. Univariate churn AUC=0.52.
> - scheme_discount_pct: mean=4.2%, per-customer trend=-1.1% (declining). Univariate churn AUC=0.64.
>
> CATEGORICAL FIELDS:
> - product_group: top 5 = Adhesives (42%), Waterproofing (28%), Tile Grout (15%), Sealants (10%), Other (5%). Per-customer diversity: mean=2.1. Churn rate: Sealants customers churn at 34% vs 18% overall.
> - payment_terms: Net 30 (55%), COD (30%), Net 45 (15%). Churn rate: Net 45 = 31%, COD = 12%.
>
> DATETIME FIELDS:
> - invoice_date: median purchase gap = 32 days, seasonal index: Dec=1.4x, Jun=0.6x.
>
> CHURN WINDOW TEST:
> - 60 days: F1=0.78 (best), churn rate=28%
> - 90 days: F1=0.71, churn rate=19%
> - 30 days: discarded (churn rate=82%)
>
> CROSS-FILE:
> - Loyalty data covers 68% of transaction customers
> - Correlation between points earned and purchase value: r=0.73
>
> What type of business is this? What patterns should we focus on?"

The LLM now receives computed facts about every field, not just column names. Its hypothesis will reference specific findings: "Sealants customers churn at 34% — this may indicate a product-line issue. Net 45 payment terms correlate with higher churn — credit pressure."

### 3d. Show User Findings (Not MCQs)

**Current:** Show MCQs, user answers, pipeline uses answers.

**Proposed:** Show computed findings, user confirms or corrects.

The findings are now richer because every field was analyzed:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  What we found in your data                              │
│                                                          │
│  Purchase pattern: Most customers order every 30-45      │
│  days. 22% have ordered only once.                       │
│                                                          │
│  Churn threshold: Customers who go 60 days without       │
│  ordering are unlikely to return. We tested 6            │
│  thresholds and 60 days produced the clearest signal.    │
│                                                          │
│  Seasonality: December orders are 40% above average.     │
│  June is 40% below.                                     │
│                                                          │
│  Revenue concentration: Your top 20% of customers        │
│  account for 74% of revenue.                             │
│                                                          │
│  Signals we found in your data:                          │
│  • Customers on "Net 45" payment terms churn at 2.6x     │
│    the rate of COD customers.                            │
│  • Customers buying Sealants churn at 34% vs 18%         │
│    overall.                                              │
│  • Declining scheme discounts correlate with churn        │
│    (AUC 0.64).                                           │
│                                                          │
│  Loyalty data: We found a 0.73 correlation between       │
│  loyalty point earnings and purchase value. Customers    │
│  who stop earning points tend to reduce purchases        │
│  within 2-3 months.                                      │
│                                                          │
│  Does this match what you see?  [Yes] [Let me correct]   │
│                                                          │
│  Anything else we should know?                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ e.g. "We had a price increase in March that caused │  │
│  │ some dealers to hold off ordering"                 │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

The "Signals we found" section is new. Because every field was analyzed, we can surface findings the user did not ask for and would not have known to ask about. This is the first "wow" — the system found something in their data they did not know.

**Which signals to surface:** Show the top 3-5 findings ranked by univariate churn AUC from the field analysis. Only show findings with AUC > 0.55 (above random). The LLM rewrites the statistical finding into plain language: "Univariate AUC 0.64 for scheme_discount_pct_trend with negative slope" becomes "Declining scheme discounts correlate with churn."

**Why this is better:**
- The VP can verify these statements against what they know. "Yes, our top 20% are 74% of revenue — that sounds right." Trust starts here, before the model even trains.
- The VP sees signals they did not expect. "We didn't know payment terms correlated with churn." This is insight before the model trains.
- The VP does not need to translate their knowledge into MCQ answers. They review findings and correct errors.
- The free-text box captures domain context the data cannot show: price changes, competitor events, seasonal disruptions, field team changes.

**If user clicks "Let me correct":** Show MCQs with defaults pre-filled from computed values. The user overrides only what is wrong.

### 3e. MCQs (Override Only)

MCQs appear only when the user clicks "Let me correct." Defaults are computed from the field analysis:

| Question | Default Source |
|----------|---------------|
| "What is your typical purchase cycle?" | Median inter-purchase gap from datetime analysis |
| "After how many days of no orders is a customer considered lost?" | Auto-selected churn window (best F1) |
| "Is your business seasonal?" | Seasonal index from datetime analysis (flag if any month > 1.3x or < 0.7x) |
| "Do your customers buy many product categories or one?" | Per-customer diversity from categorical analysis |

Type-specific questions appear only if the corresponding data type was uploaded:

| Data Type | Question | Default Source |
|-----------|----------|---------------|
| Service | "How often do customers use after-sales service?" | Frequency analysis on ticket_date field |
| Loyalty | "What does your program reward?" | Concentration analysis on transaction_type field |
| Returns | "What is your typical return rate?" | Per-customer profile of return_quantity field |
| Field | "How often do reps visit each customer?" | Frequency analysis on visit_date field |

---

## Stage 4: Revised Flow

### 4a. Feature Matrix Already Computed

The exhaustive field analysis in Stage 3a already produced a per-customer feature matrix. Stage 4 does not recompute features from scratch. It receives the matrix and adds to it:

**Already computed (from 3a):**
- All per-customer features from numeric fields (~3 features per numeric column)
- All per-customer features from categorical fields (~3 features per categorical column)
- All per-customer features from datetime fields (~7 features per datetime column)

**Added in 4a:**
- Cross-source features (if multi-file): engagement-purchase ratio, service-to-purchase ratio, visit-to-order conversion, etc.
- Per-customer adaptive gap: `gap_vs_personal_median`
- Interaction features between high-signal fields (if two fields both have univariate AUC > 0.60, compute their ratio and product as additional features)

**The tier system becomes a labeling system, not a gating system:**
- Tier 1 = features derived from the field mapped as `transaction_date` + field mapped as `amount` + field mapped as `customer_id`. These are the standard RFM features.
- Tier 2 = features derived from fields mapped as `product`, `category`, `channel`, `region`.
- Tier 3 = features derived from secondary file fields (service, loyalty, returns, field).
- Tier 4 = features derived from fields mapped as `other` — these are the signals nobody asked for.

All tiers are computed. The tier label is used for attribution in results ("60% of signal came from Tier 1, 25% from Tier 3, 15% from Tier 4"), not for deciding what to compute.

### 4b. Statistical Pruning (Fast, No Model Needed)

```
1. Drop features with zero variance (constant across all customers)
2. Compute pairwise Pearson correlation matrix
3. For pairs with |r| > 0.95:
   a. Compute univariate AUC of each against the label
   b. Drop the one with lower AUC
4. Drop features with >90% null values
```

This reduces the feature set by 20-40%. From ~80 features to ~50-60. Fast (correlation matrix on 80 features takes <1 second).

### 4c. Leakage Detection (Semantic, Not Name-Based)

**Current:** Evaluator checks feature names against label definition. `recency` gets flagged (sometimes). `recent_revenue_ratio` does not.

**Proposed: Three-layer leakage detection.**

**Layer 1: Statistical detection**
```
For each feature:
    Compute univariate AUC against label
    If AUC > 0.90:
        Flag as suspect
```

A feature with 0.95 AUC by itself is either the single best predictor or it is leaking. In the exhaustive approach, `{transaction_date}_recency` will be flagged automatically because its univariate AUC against "no purchase in N days" will be near 1.0.

**Layer 2: Temporal ordering (for cross-source features)**
```
For each flagged cross-source feature:
    For customers who churned:
        signal_date = when this feature's value changed
        churn_date = last purchase date

    If median(churn_date - signal_date) > 30 days:
        → Leading indicator. Signal preceded churn. Keep.
    If median(churn_date - signal_date) ≈ 0:
        → Simultaneous. Possible leakage. Remove.
```

This distinguishes:
- **Leakage:** `recency` = days since last purchase ≈ churn label = no purchase in N days. Same measurement.
- **Leading indicator:** `days_since_last_loyalty_earn` drops 3 months before purchases stop. Real signal.

**Layer 3: Ablation test**
```
For each suspect feature:
    Train model WITH the feature
    Train model WITHOUT the feature

    If AUC drops > 0.15 when removed:
        → This feature was carrying the model
        → Remaining features cannot compensate
        → Flag: model depends on a single suspect feature

    If AUC drops < 0.05 when removed:
        → Feature was redundant with others
        → Safe to remove without model degradation
```

**Implementation:** Leakage detection runs after statistical pruning, before the main training loop. Results are stored in session and reported to the user: "We removed 'days since last purchase' because it measures the same thing as the churn definition. The model uses the remaining signals."

### 4d. Train With All Surviving Features

Same as today: XGBoost + Random Forest, 80/20 stratified split. No change to the training mechanics.

The feature matrix entering training is now:
- Exhaustive (derived from every field, not a curated subset)
- Pruned (zero-variance, high-correlation, high-null removed)
- Leakage-free (suspect features removed or confirmed as leading indicators)
- Typically 30-50 features after pruning

### 4e. Importance-Based Pruning

```
1. Get feature importances from trained model
2. Drop features below 1% importance
3. Retrain with pruned set
4. Record: features_used, features_dropped, importance_distribution
5. Tag each surviving feature with its tier (1/2/3/4) for attribution
```

### 4f. Baseline Comparison (Multi-Type Data)

For sessions with multiple data types:

```
Model A: Train with Tier 1 + Tier 2 features only (transaction-derived)
Model B: Train with all tiers (including Tier 3 from secondary files and Tier 4 from "other" fields)

Report:
    Model A F1 = 0.82
    Model B F1 = 0.91
    "Adding your loyalty data improved churn prediction F1 from 0.82 to 0.91."
    "Loyalty features account for 25% of the prediction signal."
    "Fields you might not have expected: payment_terms and scheme_discount_pct
     contribute 8% of the signal."
```

The last line is the "Tier 4 surprise" — signals from fields mapped as `other` that the selective approach would have missed entirely.

### 4g. Feature Group Attribution

Track which source each feature came from. In the results:

```
Feature importance by source:
    Transaction signals (Tier 1):    45% (purchase frequency, monetary trend, gap variability)
    Product/category (Tier 2):       15% (category concentration, product mix shift)
    Loyalty signals (Tier 3):        25% (earn trend, days since redemption, tier)
    Other fields (Tier 4):            8% (payment_terms_churn_rate, scheme_discount_pct_trend)
    Cross-source (Tier 3+):           7% (engagement-purchase ratio)
```

This tells the VP which data matters most and where to invest in data quality. The Tier 4 finding — that payment terms and scheme discounts matter — is something they would not have learned from any dashboard.

---

## The "Wow" Moments This Produces

### Moment 1: Signals Nobody Asked For

The VP sees in the findings screen: "Customers on 'Net 45' payment terms churn at 2.6x the rate of COD customers. Customers buying Sealants churn at 34% vs 18% overall."

The VP did not ask for this. Nobody told the system to look at payment terms. It analyzed every field and surfaced the ones that matter. The VP thinks: "We never connected payment terms to churn. That is worth investigating."

### Moment 2: Computed Churn Definition

The VP sees: "We tested 6 definitions of churn on your data. 60 days produced the clearest signal."

No other tool does this. They all ask or hardcode. Showing that the system tested and selected builds credibility.

### Moment 3: Backtest With Names

The VP sees: "Of 52 customers the model flagged 3 months ago, 41 stopped ordering. Here are their names."

The VP recognizes Sharma Brothers, Patel & Sons. These are real customers they lost. The model caught them.

### Moment 4: Cross-Source Leading Indicator

The VP sees: "8 of your current dealers show the same pattern as the 15 dealers you lost last quarter — their linked painters stopped earning loyalty points 3-4 months before purchases declined."

The VP thinks: "We didn't know painter engagement was connected to dealer revenue. These 8 dealers need attention now."

### Moment 5: Data Value Quantification

The VP sees: "Adding your loyalty data improved prediction from 82% to 91%. Loyalty signals account for 25% of the prediction. Fields you might not have expected — payment terms and scheme discounts — contribute 8%."

The VP thinks: "The painter program is a churn early warning system. And I should talk to the commercial team about Net 45 terms."

---

## Runtime Budget

The "5 minutes" target constrains what we can compute. Estimates for 500K transaction rows, 30 columns, 1000-5000 customers:

| Step | Time | Notes |
|------|------|-------|
| 3a. Exhaustive field analysis (30 cols × 4 analyses) | 15-30s | Pandas groupby + aggregation per field |
| 3b. Auto churn window (6 candidates) | 5-10s | Feature matrix already computed, just 6x (labels + fast XGBoost) |
| 3c. LLM hypothesis | 3-8s | Single Groq/Gemini call with full signature |
| 3d-e. User review | 10-30s | User reads findings and confirms |
| 4a. Add cross-source + interaction features | 2-5s | Small additions to existing matrix |
| 4b. Statistical pruning | 1-2s | Correlation matrix on ~80 features |
| 4c. Leakage detection | 5-10s | Univariate AUCs + ablation for flagged features |
| 4d. Main training | 5-15s | XGBoost + RF |
| 4e. Pruning + retrain | 3-8s | Subset features + retrain |
| 4f. Baseline comparison | 5-15s | Train transaction-only model |
| **Total** | **55-135s** | **Within 2.5 minutes of compute** |

User-facing time: compute + user review + agent loop iterations ≈ 3-5 minutes. Within budget.

Note: The exhaustive analysis (15-30s) replaces both the old "compute signatures" step AND the old "compute Tier 1+2+3 features" step. It is not additional work — it is the same work done once instead of twice.

---

## Risk Matrix

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Too many features from exhaustive analysis (80+ features, 200 customers) | Overfitting | Statistical pruning + correlation removal + importance pruning reduce to 20-30 features before final training. Feature-to-sample ratio monitored: if features > customers/3, apply more pruning. |
| Data signatures misleading (e.g., recent product launch skews seasonal index) | Wrong hypothesis | User review step catches it. Free text captures context. LLM prompt includes raw signatures, not interpreted ones — the LLM can reason about outliers. |
| All churn windows produce bad F1 (<0.5) | No usable model | Report to user: "Your data may not have enough signal for churn prediction. Consider adding more history or a second data type." |
| Cross-file overlap rate too low (<10%) | Tier 3 features cover too few customers | Report: "Your loyalty data covers 8% of customers. We built the model on transaction data only. Adding more loyalty coverage would improve predictions." |
| Per-customer adaptive gap produces noisy labels for low-frequency buyers | Bad labels for tail customers | Use adaptive gap as a feature, not as the label. Global window for labels. |
| Leakage detection removes a real signal | Reduced model performance | Ablation test (Layer 3) catches this: if removing the feature drops AUC significantly and temporal ordering confirms it's a leading indicator, keep it. |
| Compute time exceeds 5-minute budget | User abandons | Stream progress via WebSocket: "Analyzing 30 fields... Testing churn thresholds... Training models..." Each step shows progress. The exhaustive analysis is one pass, not 30 sequential waits. |
| Univariate churn signal analysis requires labels, but labels depend on churn window (circular) | Cannot compute Analysis #3 before churn window selected | Use a default 90-day window for the initial univariate analysis. After auto-selecting the best window in 3b, recompute univariate AUCs with the correct labels. The initial pass is approximate; the final pass is exact. |
| "Other" fields produce noise features that dilute the model | Lower signal-to-noise | This is what pruning handles. Zero-variance, high-correlation, and low-importance pruning remove noise features. The risk of missing a real signal in an "other" field outweighs the risk of computing a noise feature that gets pruned. |
