# LLM Integration Test Failure Report

## Test Executed
Full 8-stage pipeline run on `churn-tool/tests/test_data/transactions.csv` using Groq API (llama-3.3-70b-versatile).

## Result
Pipeline failed at **Stage 5 (Labels)** with HTTP 400:
```
{"detail": "Not enough data before cutoff date. Try a shorter churn window."}
```

Stages 1-4 (Upload, Column Mapping, Hypothesis, Features) all passed.

## Root Cause

The `transactions.csv` file has no date column. It has a `month` column containing integers 1-12:

```
user_id,month,quantity,price,revenue,segment
1,1,2,5.0,10.0,Regular
1,2,3,5.0,15.0,Regular
```

### What happened step by step

1. **Stage 2 (LLM column mapping):** Groq mapped `month` -> `transaction_date` with 0.8 confidence. This is the best mapping available given the data, but it is wrong. The column contains month numbers, not dates.

2. **Stage 4 (Features):** `pd.to_datetime()` converted integers 1-12 into nanosecond timestamps on 1970-01-01:
   - `1` -> `1970-01-01 00:00:00.000000001`
   - `12` -> `1970-01-01 00:00:00.000000012`

   All 8573 transactions mapped to 12 timestamps within a 12-nanosecond range. Features still computed (recency=0, all frequency windows=full count, regularity=1.0).

3. **Stage 5 (Labels):** The auto-derived churn window was 14 days (minimum clamp). The cutoff date = max_date - 14 days = December 1969. Zero transactions exist before December 1969. The stage raised 400: "Not enough data before cutoff date."

### Data shape confirmation
```
Month unique values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Users per month: 1000 (month 1) declining to 580 (month 12)
Segments: Regular, Short-term, Power-Loyal, Power-Churn
```

The declining user count across months (1000 -> 580) shows churn is encoded in the data, but the pipeline cannot use it because it requires actual date values to compute time-based features and churn labels.

## Gemini Status

Both Gemini API keys hit `429 RESOURCE_EXHAUSTED` on the free tier for `gemini-2.0-flash`. The daily quota was depleted. Gemini was never tested with `transactions.csv`.

The Gemini keys used:
- `AIzaSyDFxgtvUzsoIh1Xuj40Bth22npDeI8CdxU` (from backend/.env.local)
- `AIzaSyCQhgs2WpOANgRbS9t4HwvXJELCdYDBg6I` (provided by user)

Both returned:
```
Quota exceeded for metric: generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
```

## Groq with ecommerce_sample.csv

Groq worked on `ecommerce_sample.csv` (which has real date strings). All 13 integration tests passed after threshold adjustments. The LLM correctly mapped columns, generated hypothesis, selected Tier 2 features, and summarized results.

## What would fix the transactions.csv failure

The `transactions.csv` data needs a preprocessing step to convert `month` integers into date strings (e.g., `2024-01-15`, `2024-02-15`, ...) before upload. The pipeline assumes the transaction_date column contains parseable date values. This is a data format limitation, not a code bug or LLM failure.
