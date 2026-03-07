# Data Leakage in Churn Pipeline: Observation and Fix

## Problem

The pipeline computes features from the entire dataset, then defines churn labels using a time-based cutoff. The `recency` feature (days since last purchase) directly encodes the churn label, producing a model that memorizes instead of predicting.

### How Leakage Occurs

```
Timeline:  Jan -------- Mar -------- Nov 1 (cutoff) -------- Dec 31
                                       |
           <--- features computed from ALL data (Jan-Dec) --->
                                       |
                              Labels: no purchase after Nov 1 = churned
```

1. Stage 4 computes `recency` = `max_date - last_purchase_date` using all data including Dec.
2. Stage 5 sets cutoff = Nov 1. Users with no transaction after Nov 1 are labeled churned.
3. A user whose last transaction is March has recency = 270 days and is labeled churned.
4. A user whose last transaction is December has recency = 5 days and is labeled active.
5. `recency > churn_window` and `churned = 1` are the same condition. The feature contains the label.

### Observed Symptoms

- AUC = 1.0, F1 = 1.0, precision = 1.0, recall = 1.0
- `recency` has 100% feature importance, all other features at 0%
- 0 medium-risk users (all predictions are extreme: 99.8% or 0.2%)
- SHAP values: recency contributes +6.2 or -6.2, everything else contributes 0.0

## Fix: Observation/Prediction Time Split

Standard churn modeling separates the timeline into two non-overlapping windows:

```
Timeline:  Jan -------- Mar -------- Nov 1 (cutoff) -------- Dec 31
                                       |
           <--- observation window --->|<--- prediction window --->
           features computed here only  labels computed here only
```

### Changes

**s4_features.py:**
- Before computing features, determine the churn window and cutoff date
- Filter the dataframe to only rows in the observation window (before cutoff)
- Pass the filtered dataframe to all feature functions
- `recency` is now computed relative to the cutoff date, not the dataset end

**s5_labels.py:**
- Use the churn window computed in stage 4 (stored in session)
- Labels still computed from prediction window (after cutoff)

### Expected Outcome

- `recency` no longer encodes the label. A user with recency = 10 days (relative to cutoff) could still churn if they do not transact in the prediction window.
- Other features (frequency trend, monetary trend, purchase regularity, max gap) gain non-zero importance.
- AUC drops to a range between 0.7 and 0.95.
- Medium-risk tier has users.
- The model has predictive value on unseen data.
