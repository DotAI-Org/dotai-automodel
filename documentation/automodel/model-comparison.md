# Model Comparison: XGBoost vs Random Forest, With and Without Recency

## Dataset

`improvedTransactions.csv` — 1000 users, 6495 transactions across 2024. Users join throughout the year (not all in January). Four segments: Regular (300), Short-term (300), Power-Loyal (280), Power-Churn (120). Time-split applied: features from observation window (before Oct 31), labels from prediction window (after Oct 31).

- Users in model: 939
- Churn rate: 30.1% (283 churned, 656 active)
- Features: 14 (10 Tier 1 + 4 Tier 2)
- Train/test split: 80/20, stratified, seed=42

## Performance Summary

| Model | AUC | F1 | Precision | Recall | FP | FN |
|---|---|---|---|---|---|---|
| XGBoost + recency | 0.9707 | 0.889 | 0.941 | 0.842 | 3 | 9 |
| XGBoost - recency | 0.9733 | 0.907 | 0.961 | 0.860 | 2 | 8 |
| Random Forest + recency | 0.9747 | 0.906 | 0.980 | 0.842 | 1 | 9 |
| Random Forest - recency | 0.9792 | 0.906 | 0.980 | 0.842 | 1 | 9 |

Best configuration: **Random Forest without recency** (AUC 0.9792, 1 FP, 9 FN).

## Feature Importance

| Feature | XGB+rec | XGB-rec | RF+rec | RF-rec |
|---|---|---|---|---|
| recency | 61.1% | N/A | 27.4% | N/A |
| frequency_30d | 0.0% | 80.1% | 22.2% | 28.1% |
| frequency_60d | 1.5% | 2.5% | 11.4% | 21.5% |
| frequency_90d | 0.7% | 0.7% | 8.7% | 13.5% |
| monetary_total | 6.9% | 3.5% | 2.5% | 3.0% |
| monetary_avg | 0.0% | 0.0% | 0.0% | 0.0% |
| frequency_trend | 2.2% | 2.5% | 5.7% | 8.1% |
| monetary_trend | 1.6% | 0.8% | 1.8% | 2.2% |
| days_between_purchases_avg | 4.7% | 1.5% | 3.5% | 4.0% |
| days_between_purchases_std | 5.3% | 1.9% | 3.6% | 3.8% |
| avg_basket_size | 7.5% | 2.9% | 5.8% | 7.8% |
| order_size_trend | 0.0% | 0.0% | 2.1% | 1.0% |
| max_gap_between_purchases | 4.9% | 2.0% | 2.6% | 3.6% |
| purchase_regularity_score | 3.6% | 1.7% | 2.7% | 3.6% |

## Observations

### 1. Removing Recency Improves the Model

Recency measures "days since last purchase relative to cutoff." After the time-split fix, it is no longer a direct leak, but it still correlates with the label enough to dominate XGBoost (61.1%). Removing it forces the model to use behavioral features (frequency, trends, regularity), which produce equal or better metrics:

- XGBoost AUC: 0.9707 → 0.9733 (+0.0026)
- XGBoost F1: 0.889 → 0.907 (+0.018)
- XGBoost FP: 3 → 2

### 2. Random Forest Outperforms XGBoost on This Dataset

Random Forest wins on AUC and precision in all configurations. The gap is small (0.004-0.006 AUC) but consistent.

Why: RF builds 100 independent trees, each seeing a random subset of features. No single feature can dominate across all trees. XGBoost builds trees sequentially and concentrates on the best splitter — 61.1% on recency or 80.1% on frequency_30d.

RF distributes importance: frequency_30d (28%), frequency_60d (22%), frequency_90d (14%), frequency_trend (8%), avg_basket_size (8%). Five features above 5%.

XGBoost concentrates: frequency_30d (80%) when recency is removed. The remaining 12 features share 20%.

On larger, noisier datasets with complex feature interactions, XGBoost typically outperforms RF. On this dataset (939 users, clean segments), RF's built-in feature decorrelation is an advantage.

### 3. monetary_avg Has Zero Importance

Every user buys at the same price (5.0). The feature has zero variance and contributes nothing in all 4 configurations. Variable pricing in the dataset would make this feature useful.

### 4. Precision vs Recall Tradeoff

RF has higher precision (0.980 vs 0.941-0.961) and equal or lower recall (0.842 vs 0.842-0.860). RF is more conservative — fewer false positives (1 vs 2-3) but same false negatives (9 vs 8-9). For a business that wants to minimize wasted retention spend on non-churning customers, RF is the better choice.
