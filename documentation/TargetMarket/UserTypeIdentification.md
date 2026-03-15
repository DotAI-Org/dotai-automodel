# User Type Identification and Multi-Data-Type Pipeline Changes

## Problem

The tool today handles Type 1 data: transaction CSVs. A user uploads one file, the pipeline builds a churn model from purchase recency, frequency, and monetary patterns.

But most target verticals have more than transactions. Paints companies have painter loyalty data. Consumer durables companies have service records. Pharma companies have MR call reports. The DataPoints doc defines 5 data types. Each type changes what the pipeline can compute, what models make sense, and what the output looks like.

This document covers: how we identify which type the user has, how we ask for the data, how each type changes each pipeline stage, what features to pre-compute, and what models to build.

---

## The 5 Data Types (recap)

| Type | Data | Example Verticals |
|------|------|-------------------|
| 1 | Transaction-only | FMCG, dairy, steel pipes, textiles, footwear, telecom |
| 2 | Transaction + service/warranty | Auto OEM, consumer durables, tyres, batteries, equipment |
| 3 | Transaction + loyalty/membership | Paints, cement, wires, lubricants, adhesives, auto aftermarket |
| 4 | Transaction + returns/delivery | Dairy (perishable), D2C, subscription, pharma, tiles, apparel |
| 5 | Transaction + field interaction | Adhesives, pharma, agri, FMCG (field force), cement |

Many companies overlap (e.g., Pidilite = Type 1 + 3 + 5). The system must handle combinations.

---

## Part 1: How We Identify the User Type

### Step 1: File Upload — UI Affordance for Describing Files

The multi-file upload screen already has a text input for describing the files. This is not enough. A free-text box gives no structure and most users will write something vague like "sales data and loyalty data."

**Proposed UI change:**

After the user drops files, show a per-file description panel. For each uploaded file, display:

```
┌─────────────────────────────────────────────────────────┐
│  File 1: primary_sales_2024.csv  (34,892 rows)          │
│                                                          │
│  What is this file?                                      │
│                                                          │
│  ○ Transaction / purchase orders / invoices              │
│  ○ Service / warranty / complaint records                │
│  ○ Loyalty / points / membership data                    │
│  ○ Returns / damage / expiry records                     │
│  ○ Field visits / call reports / engagement logs         │
│  ○ Customer / dealer master (profile data)               │
│  ○ Other                                                 │
│                                                          │
│  Optional: describe in your own words                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  How does this file connect to the others?               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ e.g. "dealer_code in this file matches             │  │
│  │ distributor_code in the sales file"                │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Why radio buttons instead of free text alone:**
- The 6 radio options map to the data types the system knows how to process
- Selection triggers the right feature catalog and join logic downstream
- The user does not need to know our internal taxonomy — the labels use their language
- "Other" with a free-text fallback handles edge cases
- The "how does this file connect" prompt guides the user to name the join key without requiring database vocabulary

**The free-text box stays** — it captures context the radio buttons miss (e.g., "this is North region only" or "last 18 months of data").

### Step 2: Column Mapping Confirms the Type

After upload, Stage 2 (column mapping) already runs. Today it maps columns to: `customer_id`, `transaction_date`, `amount`, `product`, `quantity`, `category`, `channel`, `region`, `other`.

**New column roles to add per data type:**

| Data Type | New Roles |
|-----------|-----------|
| Service (Type 2) | `ticket_id`, `ticket_date`, `resolution_date`, `complaint_category`, `warranty_status`, `csat_score`, `tat_days` |
| Loyalty (Type 3) | `member_id`, `points_earned`, `points_redeemed`, `tier`, `enrollment_date`, `transaction_type` |
| Returns (Type 4) | `return_id`, `return_date`, `return_reason`, `return_quantity`, `original_invoice` |
| Field (Type 5) | `visit_id`, `visit_date`, `entity_type`, `visit_duration`, `order_booked`, `objective` |
| Master | `dealer_code`, `dealer_name`, `registration_date`, `status`, `credit_limit`, `tier`, `territory` |

The LLM column mapper receives the user's radio button selection as context. This narrows the role search space and increases mapping accuracy.

### Step 3: LLM Cross-File Analysis

After column mapping completes for all files, the LLM receives:
- Per-file: column names, roles, row counts, sample values
- Per-file: user's radio selection and free-text description
- User's description of how files connect

The LLM produces:
1. **Confirmed data type** (Type 1-5 combination)
2. **Join strategy** (which columns connect the files — this already exists in `s2_column_map.join_files`)
3. **Summary for the user** — "You uploaded transaction data and loyalty program data. We will join them on dealer_code to build a model that uses both purchase patterns and engagement signals."

The user reviews this summary and confirms or corrects.

---

## Part 2: How Each Data Type Changes the Pipeline

### Stage 1: Upload

| Change | Detail |
|--------|--------|
| Per-file radio selector | New UI component: 7 radio options per file |
| Per-file connection prompt | New UI text input per file |
| Schema: `file_type` field | Store the radio selection per file in session alongside `filename`, `df`, `profile` |
| Validation per type | Service files should have a date column and a customer/ticket ID. Loyalty files should have points columns. Warn if expected columns are missing for the declared type. |

### Stage 2: Column Mapping

| Change | Detail |
|--------|--------|
| Extended role enum | Add ~25 new roles across the 5 types (listed above) |
| Type-aware prompt | Include the user's file type selection in the LLM prompt. "This file was described as service/warranty data. Map columns accordingly." |
| Cross-file summary | After mapping all files, produce a human-readable summary of what was found and how files relate |
| Join strategy | Already exists. No change needed except: pass file type to the join LLM so it can make better join decisions (e.g., for loyalty data, join on `member_id = dealer_code`) |

### Stage 3: Hypothesis

| Change | Detail |
|--------|--------|
| Type-aware hypothesis | The LLM receives which data types are present. Its hypothesis includes not just business type but data richness: "You have transaction + loyalty data. This allows us to use engagement signals as leading indicators of churn." |
| Type-specific MCQs | New questions per type. See below. |
| Churn entity identification | With multiple entity types (dealers AND influencers), the LLM must ask: "Who do you want to predict churn for? Dealers, influencers, or both?" |

**New MCQs by type:**

| Type | Questions |
|------|-----------|
| Type 2 (service) | "How often do your customers use after-sales service?" / "Is warranty renewal a revenue stream?" / "What is an acceptable complaint resolution time?" |
| Type 3 (loyalty) | "What does your loyalty program reward — purchases, referrals, training attendance?" / "How many tiers does your program have?" / "What is the typical redemption cycle?" |
| Type 4 (returns) | "What is your typical return rate?" / "Are returns mostly damage, expiry, or unsold?" / "Do returns happen within a fixed window?" |
| Type 5 (field) | "How often do your reps visit each customer?" / "Do visits drive orders or are they independent?" / "Do you track influencer recommendations?" |

### Stage 4: Feature Engineering

This is the stage with the largest changes. Each data type adds a new tier of features.

**Current state:** Tier 1 (10 features from transactions), Tier 2 (12 features from transactions + optional columns), DSL features (LLM-suggested).

**Proposed:** Add Tier 3 — pre-built features per data type. The LLM selects which Tier 3 features to compute based on the data type and hypothesis.

Features listed in Part 3 below.

### Stage 5: Label Generation

| Change | Detail |
|--------|--------|
| Multi-entity labels | If the user wants to predict churn for influencers (not dealers), labels must be computed from the influencer's activity, not the dealer's. The `customer_id` column changes based on the target entity. |
| Compound labels | For Type 2 (service), churn might mean "no purchases AND no service visits." For Type 3 (loyalty), churn might mean "no purchases AND no points earned." The label definition becomes configurable based on data type. |
| Leading indicator labels | For Type 3/5, we can build a second model: predict future transaction churn from current engagement drop. Label = "dealer whose purchases dropped >50% in next quarter." Features = loyalty/field engagement from current quarter. |

### Stage 6: Model Training

| Change | Detail |
|--------|--------|
| Feature groups | Track which features come from which data type. Report feature importance grouped by source: "60% of prediction signal comes from transaction features, 25% from loyalty features, 15% from service features." |
| Multiple models | For companies with influencer data (Type 3/5), build two models: (a) dealer churn from transactions, (b) dealer churn from influencer engagement signals. Compare whether adding influencer data improves predictions. See Part 4. |
| Baseline comparison | Train a transaction-only model first, then a combined model. Show the lift from adding the second data type. This is the sales argument: "Adding your loyalty data improved prediction accuracy from X to Y." |

### Stage 7: Results / LLM Evaluation

| Change | Detail |
|--------|--------|
| Multi-source explanation | "What Changed" column in the customer list now draws from multiple data types. Instead of just "purchase frequency declining," it can say "purchase frequency declining AND loyalty points redemption stopped 3 months ago." |
| Data type contribution | Show which data source contributed most to each prediction. "For Sharma Brothers, 70% of the risk signal came from declining purchases, 30% from lapsed loyalty engagement." |
| Backtest with richer context | The backtest list includes signals from all data types: "Sharma Brothers — last order 38 days ago, last points redemption 90 days ago, last service call 6 months ago." |

### Stage 8: Inference

| Change | Detail |
|--------|--------|
| Richer "What Changed" | Per-customer top features now span multiple data types |
| Entity-specific output | If predicting influencer churn, output is influencer names, not dealer names |
| Action recommendations | With richer data, the tool can suggest type-specific actions: "This dealer's loyalty points are about to expire — trigger a redemption reminder" vs "This dealer has 3 open service complaints — resolve before expecting new orders" |

---

## Part 3: Pre-Computed Features by Data Type

### Type 2: Service/Warranty Features

Computed from: `service_records.csv`, `amc_contracts.csv`

| # | Feature | What It Measures | Required Columns |
|---|---------|-----------------|-----------------|
| 1 | `service_ticket_count` | Total service tickets raised | ticket_id, customer_code |
| 2 | `service_ticket_count_90d` | Tickets in last 90 days | ticket_id, ticket_date |
| 3 | `avg_resolution_tat` | Mean days from complaint to resolution | ticket_date, resolution_date |
| 4 | `max_resolution_tat` | Worst resolution time | ticket_date, resolution_date |
| 5 | `open_ticket_count` | Unresolved tickets | closure_status |
| 6 | `csat_avg` | Mean satisfaction score | csat_score |
| 7 | `csat_trend` | CSAT in recent half minus first half | csat_score, ticket_date |
| 8 | `warranty_active` | Whether any product is under warranty | warranty_status |
| 9 | `warranty_expiring_soon` | Warranty expires within 90 days | warranty_expiry_date |
| 10 | `escalation_rate` | % of tickets escalated or reopened | closure_status |
| 11 | `repeat_complaint_rate` | % of tickets for same issue type | issue_type, customer_code |
| 12 | `amc_renewal_status` | Whether AMC is active, expired, or due | renewal_status |
| 13 | `amc_visits_remaining` | Scheduled visits not yet completed | visits_included, visits_completed |
| 14 | `parts_cost_total` | Total cost of parts replaced | parts_cost |
| 15 | `service_to_purchase_ratio` | Service tickets per purchase | ticket_count / purchase_count |

**Churn signal:** Declining CSAT, increasing TAT, expiring warranty without renewal, open escalations.

### Type 3: Loyalty/Membership Features

Computed from: `loyalty_ledger.csv`, `loyalty_transactions.csv`, `influencer_master.csv`, `influencer_purchases.csv`

| # | Feature | What It Measures | Required Columns |
|---|---------|-----------------|-----------------|
| 1 | `points_earned_total` | Lifetime points earned | total_points_earned |
| 2 | `points_earned_90d` | Points earned in last 90 days | transaction_date, points |
| 3 | `points_redeemed_total` | Lifetime points redeemed | total_points_redeemed |
| 4 | `points_balance` | Current unredeemed balance | current_balance |
| 5 | `earn_to_redeem_ratio` | Points earned / points redeemed | total_points_earned, total_points_redeemed |
| 6 | `days_since_last_earn` | Recency of last earn transaction | last_earn_date |
| 7 | `days_since_last_redeem` | Recency of last redemption | last_redeem_date |
| 8 | `redemption_frequency` | Redemptions per quarter | transaction_type, transaction_date |
| 9 | `tier_level` | Current tier (encoded: Bronze=1, Silver=2, Gold=3, Platinum=4) | tier |
| 10 | `tier_change` | Tier upgrade/downgrade in observation window | tier (requires history) |
| 11 | `points_expiring_soon` | Points expiring within 60 days | points_expiry_date |
| 12 | `engagement_score` | Composite: earn frequency + redeem frequency + tier | computed |
| 13 | `earn_trend` | Points earned in recent half minus first half | transaction_date, points |
| 14 | `influencer_purchase_count` | SKU-level purchases by the influencer | influencer_purchases |
| 15 | `influencer_purchase_trend` | Influencer purchase value recent vs prior | transaction_date, amount |
| 16 | `training_attendance_count` | Workshops/certifications attended | training_attendance |
| 17 | `days_since_last_training` | Recency of last training event | event_date |
| 18 | `influencer_tenure_days` | Days since enrollment | registration_date |

**Churn signal:** Declining earn rate, lapsed redemption, points expiring without use, dropped tier, stopped attending training.

### Type 4: Returns/Delivery Features

Computed from: `returns.csv`, `delivery_records.csv`

| # | Feature | What It Measures | Required Columns |
|---|---------|-----------------|-----------------|
| 1 | `return_count_total` | Total returns | return_id |
| 2 | `return_count_90d` | Returns in last 90 days | return_date |
| 3 | `return_rate` | Returns / total purchases | return_count / purchase_count |
| 4 | `return_value_rate` | Return value / total purchase value | return_value / purchase_value |
| 5 | `return_reason_diversity` | Distinct return reasons | return_reason |
| 6 | `damage_return_rate` | % of returns that are damage/defect | return_reason |
| 7 | `expiry_return_rate` | % of returns that are expiry | return_reason |
| 8 | `return_trend` | Returns in recent half minus first half | return_date |
| 9 | `avg_delivery_tat` | Mean order-to-delivery days | delivery_date, received_date |
| 10 | `max_delivery_tat` | Worst delivery time | tat_days |
| 11 | `delivery_shortage_rate` | Shortage qty / dispatched qty | shortage_qty, dispatched_qty |
| 12 | `transit_damage_rate` | Transit damage qty / dispatched qty | transit_damage_qty |
| 13 | `delivery_tat_trend` | TAT in recent half minus first half | delivery_date, tat_days |
| 14 | `credit_note_count` | Number of credit notes issued | credit_note_number |
| 15 | `credit_note_value_rate` | Credit note value / purchase value | credit_note_amount |

**Churn signal:** Rising return rate, increasing delivery TAT, frequent damage/shortage, growing credit notes relative to purchases.

### Type 5: Field Interaction Features

Computed from: `visit_reports.csv`, `mr_call_reports.csv`, `training_attendance.csv`

| # | Feature | What It Measures | Required Columns |
|---|---------|-----------------|-----------------|
| 1 | `visit_count_total` | Total rep visits received | visit_id |
| 2 | `visit_count_90d` | Visits in last 90 days | visit_date |
| 3 | `avg_visit_duration` | Mean visit duration in minutes | duration_minutes |
| 4 | `days_since_last_visit` | Recency of last rep visit | visit_date |
| 5 | `visit_frequency_trend` | Visits in recent half minus first half | visit_date |
| 6 | `order_booking_rate` | % of visits that resulted in an order | order_booked |
| 7 | `order_booking_trend` | Order booking rate recent vs prior | order_booked, visit_date |
| 8 | `avg_visit_order_value` | Mean order value on visits where orders were placed | order_value |
| 9 | `payment_collection_rate` | Visits with payment collected / total visits | payment_collected |
| 10 | `competitor_activity_mentions` | Count of visits noting competitor activity | competitor_activity_noted |
| 11 | `display_compliance_rate` | % of audits where display was compliant | display_compliance |
| 12 | `mr_call_count` | MR calls to this doctor (pharma) | call_id |
| 13 | `mr_call_trend` | Calls in recent half minus first half | call_date |
| 14 | `rx_commitment_positive_rate` | % of calls where doctor said "will prescribe" | rx_commitment |
| 15 | `samples_given_count` | Total samples distributed | samples_given |
| 16 | `competitor_rx_mentions` | Count of calls noting competitor prescriptions | competitor_products_prescribed |

**Churn signal:** Declining visit frequency from reps, lower order booking rate per visit, competitor activity increasing, doctor commitment shifting away.

### Master Data Features (applies to all types)

Computed from: `dealer_master.csv`, `influencer_master.csv`

| # | Feature | What It Measures |
|---|---------|-----------------|
| 1 | `tenure_days` | Days since registration |
| 2 | `credit_utilization` | Outstanding / credit limit |
| 3 | `dealer_tier_encoded` | Gold=3, Silver=2, Bronze=1 |
| 4 | `is_active` | Status = Active |
| 5 | `competitor_brands_count` | Number of competitor brands stocked |
| 6 | `channel_type_encoded` | Dealer/sub-dealer/retailer/stockist |

---

## Part 4: Models to Build

### Model A: Transaction Churn (exists today)

- **Input:** Tier 1 + Tier 2 features from transactions
- **Label:** No purchase after cutoff date
- **Output:** Per-customer churn probability
- **Available for:** All types (Type 1-5)

This is the baseline. Always built first.

### Model B: Enriched Churn

- **Input:** Tier 1 + Tier 2 + Tier 3 features from the secondary data type
- **Label:** Same as Model A (no purchase after cutoff)
- **Output:** Per-customer churn probability with richer feature set
- **Available for:** Types 2-5
- **Purpose:** Show lift over Model A. "Adding loyalty data improved F1 from 0.82 to 0.91."

This is Model A plus the additional features. The pipeline trains both and compares.

### Model C: Engagement Churn (Type 3 and 5)

- **Input:** Loyalty/field features only (Tier 3)
- **Label:** Purchase decline >50% in next quarter (not binary churn — a regression or threshold-based classification)
- **Output:** Per-customer engagement risk score
- **Available for:** Type 3 (loyalty), Type 5 (field)
- **Purpose:** Predict purchase decline from engagement signals before it shows in transactions. This is the "leading indicator" model.

**Why this matters:** A painter who stops earning loyalty points in Q1 will stop recommending the brand in Q2, causing the dealer's purchases to drop in Q3. By the time transaction churn is visible, the root cause happened 6 months ago. Model C catches it at the engagement level.

### Model D: Influencer-to-Dealer Propagation (Type 3 and 5)

- **Input:** Aggregated influencer engagement per dealer (e.g., average painter points earned per dealer, number of active influencers per dealer)
- **Label:** Dealer purchase decline
- **Output:** Dealer risk score driven by influencer signals
- **Available for:** Paints, adhesives, cement, wires, pharma (companies with influencer programs)
- **Purpose:** Connect influencer disengagement to dealer revenue impact

**Feature examples for Model D:**
- `avg_influencer_earn_rate_per_dealer` — mean points earned by influencers linked to this dealer
- `influencer_churn_rate_per_dealer` — % of linked influencers who stopped earning
- `active_influencer_count` — influencers with activity in last 90 days
- `influencer_training_attendance_rate` — % of linked influencers attending workshops

### Model E: Service-Driven Churn (Type 2)

- **Input:** Service features + transaction features
- **Label:** Same as Model A
- **Output:** Per-customer churn probability with service signals
- **Available for:** Auto OEM, consumer durables, equipment
- **Purpose:** Identify customers whose poor service experience is driving them away, separate from purchase pattern analysis

### Model Selection Logic

The pipeline does not ask the user which model to build. It builds all applicable models based on the detected data types and presents results:

```
Data detected: Transaction + Loyalty
Models built:
  Model A (transactions only):      F1 = 0.82, AUC = 0.87
  Model B (transactions + loyalty):  F1 = 0.91, AUC = 0.93  ← selected
  Model C (engagement risk):         Identified 23 influencers at risk

"Adding your loyalty data improved churn prediction F1 from 0.82 to 0.91.
 23 influencers are showing early disengagement signals."
```

---

## Part 5: Pipeline Changes Summary

### Frontend Changes

| # | Change | Screen | Detail |
|---|--------|--------|--------|
| 1 | Per-file radio selector | Upload (Screen 1) | 7 radio options: Transaction, Service, Loyalty, Returns, Field, Master, Other |
| 2 | Per-file connection text | Upload (Screen 1) | Text input: "How does this file connect to the others?" |
| 3 | Cross-file summary | Data Summary (Screen 1b) | Show detected data types, join strategy, and what each file contributes |
| 4 | Data type contribution | Results (Screen 4) | Show which data source contributed to each prediction |
| 5 | Multi-source "What Changed" | Customer List (Screen 4d) | "Purchase frequency declining AND loyalty engagement lapsed" |
| 6 | Model comparison | Model Details (Screen 4f) | Show Model A vs Model B performance side-by-side |
| 7 | Engagement risk section | Results (Screen 4) | If Model C was built, show influencer risk list |

### Backend Changes

| # | Change | File(s) | Detail |
|---|--------|---------|--------|
| 1 | Store `file_type` per file | `s1_upload.py`, schemas | Add `file_type` field to each entry in `session["dataframes"]` |
| 2 | Extend column role enum | `schemas.py`, `s2_column_map.py` | Add ~25 new roles for service, loyalty, returns, field, master columns |
| 3 | Type-aware mapping prompt | `s2_column_map.py` | Pass `file_type` to the LLM prompt for each file |
| 4 | Churn entity selection | `s3_hypothesis.py` | Add MCQ: "Who do you want to predict churn for?" if multiple entity types detected |
| 5 | Type-specific MCQs | `s3_hypothesis.py` | Add 3-4 MCQs per data type (service frequency, loyalty structure, return patterns, visit cadence) |
| 6 | Tier 3 feature catalog | New: `app/features/tier3_service.py`, `tier3_loyalty.py`, `tier3_returns.py`, `tier3_field.py`, `tier3_master.py` | Pre-built feature functions, same pattern as Tier 1/2 |
| 7 | Feature group tracking | `s4_features.py`, `agent/loop.py` | Track which features come from which data source |
| 8 | Compound label support | `s5_labels.py` | Allow label definition from multiple signals (e.g., no purchase AND no engagement) |
| 9 | Multi-model training | `s6_train.py`, `agent/loop.py` | Train Model A (baseline) + Model B (enriched) + Model C/D/E if applicable |
| 10 | Model comparison output | `s7_results.py` | Report lift from adding secondary data. Group feature importance by source. |
| 11 | Multi-source SHAP | `s8_inference.py` | Per-customer top features span multiple data types |

### Database Changes

| # | Change | Detail |
|---|--------|--------|
| 1 | `file_type` column | Add to session metadata (or store in the `dataframes` JSON blob) |
| 2 | `detected_data_types` | List of Type 1-5 detected for this session |
| 3 | `model_results` expansion | Store results for multiple models (A, B, C, D, E) per session |
| 4 | `engagement_predictions` | If Model C/D built, store influencer/engagement risk scores |

---

## Part 6: Join Strategy by Data Type Combination

The join logic already exists in `s2_column_map.join_files`. Below documents the expected join patterns so the LLM has examples.

| Combination | Left | Right | Join Key | Join Type | Notes |
|-------------|------|-------|----------|-----------|-------|
| Txn + Master | primary_sales | dealer_master | distributor_code = dealer_code | left | Enrich transactions with dealer profile |
| Txn + Service | primary_sales | service_records | distributor_code = customer_code | left | Not all customers have service tickets |
| Txn + Loyalty | primary_sales | loyalty_ledger | distributor_code = member_id | left | Loyalty members are a subset of all customers |
| Txn + Returns | primary_sales | returns | invoice_number = original_invoice_number | left | Join at invoice level, then aggregate per customer |
| Txn + Field | primary_sales | visit_reports | distributor_code = entity_code | left | Visit data is per-entity, sales is per-invoice |
| Txn + Influencer | primary_sales | influencer_purchases | distributor_code = dealer_code | left | Aggregate influencer activity per dealer |
| Loyalty + Influencer | loyalty_ledger | influencer_master | member_id = influencer_id | inner | For influencer-level churn prediction |

**Join is not always at the same grain.** Transaction data is at invoice-line level. Service data is at ticket level. Loyalty data is at member level. The pipeline must aggregate to the right grain (per-customer) before joining feature matrices — not join the raw tables directly.

**Proposed approach:** Do not join raw DataFrames. Instead:
1. Compute Tier 1+2 features from transaction data → per-customer feature matrix
2. Compute Tier 3 features from secondary data → per-customer feature matrix
3. Join the feature matrices on customer_id (left join, transaction customers as base)

This avoids grain mismatches and keeps the existing feature computation logic intact.

---

## Part 7: Implementation Order

**Phase 1: UI + Identification (no model changes)**
1. Add per-file radio selector and connection prompt to upload screen
2. Pass file_type to column mapping LLM prompt
3. Add cross-file summary to data summary screen
4. Store detected data types in session

**Phase 2: Type 3 (Loyalty) — highest value, most target companies**
1. Build Tier 3 loyalty features (18 features listed above)
2. Add loyalty-specific MCQs to hypothesis stage
3. Train Model B (enriched) alongside Model A (baseline)
4. Show lift comparison in results
5. Add multi-source "What Changed" to customer list

**Phase 3: Type 5 (Field) — overlaps with loyalty companies**
1. Build Tier 3 field features (16 features)
2. Build Model D (influencer-to-dealer propagation)
3. Add influencer risk output

**Phase 4: Type 2 (Service) and Type 4 (Returns)**
1. Build Tier 3 service features (15 features) and returns features (15 features)
2. Build Model E (service-driven churn)
3. Add compound label support

**Why this order:**
- Type 3 (loyalty) targets the most companies on the CompanyList (paints, cement, wires, lubricants, adhesives, auto aftermarket) and has the clearest "leading indicator" value
- Type 5 (field) overlaps with Type 3 companies (Pidilite, Asian Paints, UltraTech all have both)
- Types 2 and 4 are distinct verticals (auto OEM, consumer durables, pharma) — build after the core multi-type infrastructure is in place
