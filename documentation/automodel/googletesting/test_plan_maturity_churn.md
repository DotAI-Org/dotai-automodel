# Test Plan: Maturity-Based Churn Prediction

## Objective
To verify the AutoModel system's ability to detect a specific churn pattern: customers who leave after exactly 3 transactions due to "lack of product maturity."

## Simulation Strategy
We will generate a synthetic dataset with two distinct cohorts:

1.  **Healthy Cohort (100 users):**
    *   Transactions: 10–20 per user.
    *   Timeline: Spread across the entire year (2025).
    *   Expected Label: Active (0).

2.  **Churn Cohort (100 users):**
    *   Transactions: Exactly 3 per user.
    *   Timeline: Transactions occur within the first month of their start date, then stop.
    *   Expected Label: Churned (1).

## Pipeline Verification Steps
1.  **Stage 1 (Upload):** Ensure the 200 users and their transactions are parsed correctly.
2.  **Stage 2 (Mapping):** Verify Gemini correctly identifies semantic roles.
3.  **Stage 3 (Hypothesis):** Observe if Gemini detects a "SaaS" or "Subscription" like trial-and-drop pattern.
4.  **Stage 5 (Labeling):** Confirm the churn window correctly separates the early-droppers from the long-term users.
5.  **Stage 6 (Training):** Check for high AUC/F1 scores, indicating the model found the clear signal.
6.  **Stage 8 (Inference):** Validate that the 100 churned users are in the "High Risk" tier.

## Success Criteria
*   Model AUC > 0.85.
*   At least 90% of the Churn Cohort identified as High Risk.
*   "Frequency" or "Recency" identified as top feature importance.
