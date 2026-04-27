# Changes Proposed by Codex

## Objective

Turn AutoModel from a feature-iteration churn model builder into a validation-first modeling agent.

The current agent can compute features, retrain, detect obvious leakage, and pick a champion. The next level is to prove that the champion model is temporally valid, better than simple rules, stable across customer segments, calibrated enough to trust, and useful for a real call list.

The core change: champion selection should move from "best AUC/F1 after iterations" to "best defensible business model after backtesting, baselines, top-K lift, calibration, and stability checks."

## Feature-Level Change List

### 1. Add A Temporal Validation Harness

Build a new validation layer that runs rolling historical backtests instead of relying mainly on one random train/test split.

Proposed behavior:
- Generate multiple observation/prediction windows from the uploaded history.
- For each window, train only on data available before the prediction period.
- Evaluate whether the model would have found churned customers before they churned.
- Store per-window metrics and variance.
- Reject or downgrade models that only perform in one period.

Likely implementation:
- Add `app/validation/backtest.py`.
- Add schemas for `BacktestWindow`, `BacktestResult`, and `TemporalValidationReport`.
- Call this from the agent before final champion selection.

Acceptance criteria:
- Champion model includes at least 3 backtest windows when data permits.
- Results report mean and worst-window performance.
- Agent flags "insufficient history for temporal validation" when backtesting is not possible.

### 2. Redesign Churn Target Selection

Separate business-valid churn definition from model-easy churn definition.

Current risk:
- Stage 3 tests candidate churn windows and can favor the window with the best F1.
- That can select a target because it is easy to predict, not because it is operationally correct.

Proposed behavior:
- Compute reorder-cycle distribution: median, p75, p90, p95 inter-purchase gaps.
- Compute historical recovery curve: probability a customer returns after N silent days.
- Score churn windows using business plausibility, sample support, label stability, and modelability.
- Let the modelability score inform the decision, but not dominate it.
- Explain the selected target in business terms.

Likely implementation:
- Extend `app/stages/s3_churn_window.py`.
- Add `TargetDefinitionReport`.
- Store target evidence in session under `target_definition_report`.

Acceptance criteria:
- The selected churn window has a written evidence trail.
- The UI can show why the churn window was selected.
- The agent can say "no reliable churn target can be inferred" for weak data.

### 3. Add Baseline Challenger Models

Every trained model should be compared against simple, understandable baselines.

Baselines to add:
- Recency-only ranker.
- RFM score.
- Frequency-decline rule.
- Previous-period inactivity rule.
- Logistic regression on cleaned numeric features.

Proposed behavior:
- Train/run baseline challengers for every session.
- Compare champion lift against baselines at business-relevant list sizes.
- If the ML champion barely beats a simple rule, expose that instead of hiding it.

Likely implementation:
- Add `app/agent/baselines.py`.
- Add baseline results to `model_comparison`.
- Extend `app/stages/s6_train.py` and `app/agent/model_trainer.py` to return challenger metrics.

Acceptance criteria:
- Every result includes baseline performance.
- Champion selection requires meaningful lift over at least one simple baseline.

### 4. Optimize For Call-List Quality

Replace generic model-first metrics with call-list metrics.

Metrics to add:
- `precision_at_k`.
- `recall_at_k`.
- `lift_at_k`.
- `capture_rate_top_decile`.
- `expected_revenue_at_risk`.
- `expected_revenue_saved`, when revenue and intervention assumptions exist.

Proposed behavior:
- Ask or infer call capacity: top 50, top 100, top 500, or top 10 percent.
- Evaluate models based on how good the resulting call list is.
- Make top-K quality a first-class champion-selection criterion.

Likely implementation:
- Add `app/validation/topk.py`.
- Add `business_capacity` or `call_list_size` to MCQ/context schemas.
- Add top-K metrics to `TrainResponse`, agent status, and results UI.

Acceptance criteria:
- Results show how much better the top call list is than random and than baseline.
- Champion model cannot be selected on AUC alone.

### 5. Add Probability Calibration

Risk probabilities should be trustworthy, not just rank customers correctly.

Proposed behavior:
- Compute Brier score and calibration bins.
- Add reliability tables: predicted 0-20 percent, actual churn rate; 20-40 percent, actual churn rate; etc.
- Calibrate probabilities with isotonic regression or logistic calibration when enough validation data exists.
- If calibration is weak, show risk ranks but avoid overclaiming exact probabilities.

Likely implementation:
- Add `app/validation/calibration.py`.
- Store `calibration_report` and optional calibrator object.
- Apply calibrator in `app/stages/s8_inference.py`.

Acceptance criteria:
- Inference probabilities are calibrated when validation support is sufficient.
- UI can distinguish "rank confidence" from "probability confidence."

### 6. Add Segment Stability Diagnostics

A global model can look good while failing for key business segments.

Segments to evaluate when available:
- Region.
- Channel.
- Category.
- Customer size or revenue band.
- Tenure band.
- Purchase frequency band.
- Dealer/distributor type.

Proposed behavior:
- Compute performance by segment.
- Flag segments with weak sample size or poor lift.
- Include segment limitations in the evidence pack.

Likely implementation:
- Add `app/validation/segments.py`.
- Use mapped roles and high-cardinality bucketing from field analysis.
- Store `segment_stability_report`.

Acceptance criteria:
- Agent can say where the model works and where it does not.
- Champion selection penalizes unstable models.

### 7. Add Pre-Model Data Risk Gates

Before training, the agent should decide whether the dataset can support churn modeling.

Checks to add:
- Minimum customers.
- Minimum repeat customers.
- Minimum history length.
- Minimum positive and negative labels.
- Churn window observability.
- Seasonality dominance.
- ID role sanity checks.
- Date parsing confidence.
- Join quality for multi-file uploads.
- Future-state/leakage column suspicion before training.

Proposed behavior:
- Run gates after column mapping and before expensive modeling.
- Classify dataset as `ready`, `usable_with_warnings`, or `not_modelable`.
- Refuse confident output when data is not sufficient.

Likely implementation:
- Add `app/validation/data_readiness.py`.
- Call from Stage 3 after field analysis.
- Store `data_readiness_report`.

Acceptance criteria:
- Agent fails early with clear reasons for non-modelable datasets.
- Risk warnings are visible before training starts.

### 8. Replace LLM-Only Evaluation With Computed Evidence

Use the LLM as a critic and narrator, not as the judge of truth.

Proposed behavior:
- Keep LLM evaluation, but feed it computed reports:
  - leakage report
  - temporal validation
  - baseline lift
  - top-K lift
  - calibration
  - segment stability
  - data readiness
- Make final acceptance rules code-driven.
- Let the LLM explain tradeoffs and suggest next experiments.

Likely implementation:
- Extend `app/agent/evaluator.py`.
- Add `ModelEvidenceReport`.
- Update `SUCCESS_CRITERIA` to include validation gates, not just AUC/F1.

Acceptance criteria:
- A model cannot pass solely because the LLM says quality is acceptable.
- LLM output references computed evidence fields.

### 9. Add A Champion Selection Policy

Champion selection should be explicit, reproducible, and auditable.

Proposed policy:
- Hard gates:
  - no critical leakage
  - enough labeled samples
  - temporal validation possible or explicit warning
  - no catastrophic segment failure for major segments
- Ranking score:
  - top-K lift
  - worst-window backtest performance
  - calibration quality
  - baseline improvement
  - model simplicity/tie-breaker
- Output:
  - selected champion
  - rejected challengers
  - reasons for selection

Likely implementation:
- Add `app/agent/champion_policy.py`.
- Replace scattered champion selection in `app/agent/loop.py` and `app/stages/s6_train.py`.

Acceptance criteria:
- Same inputs produce same champion decision.
- Response includes why the champion won.

### 10. Generate A Model Evidence Pack

Every model run should produce a compact audit artifact.

Evidence pack contents:
- Data profile summary.
- Column mapping confidence.
- Target definition and churn window evidence.
- Observation and prediction windows.
- Data readiness report.
- Feature inventory and dropped features.
- Leakage report.
- Backtest results.
- Baseline comparison.
- Top-K call-list metrics.
- Calibration report.
- Segment stability report.
- Champion decision.
- Known limitations.

Likely implementation:
- Add `app/agent/evidence_pack.py`.
- Persist `evidence_pack` on the session.
- Add `/api/sessions/{id}/evidence` endpoint.
- Add downloadable JSON or Markdown report.

Acceptance criteria:
- A user or engineer can audit why the model was trusted.
- Evidence pack is available after every completed run.

### 11. Make Multi-File Support Real In The Modeling Path

The repo has multi-file upload and type metadata, but the deeper feature path is not fully connected.

Proposed behavior:
- Join secondary files using detected or user-confirmed keys.
- Compute service, loyalty, returns, field, and master-data features.
- Measure overlap and join loss.
- Compare transaction-only model vs enriched model.
- Attribute lift to data sources.

Likely implementation:
- Connect `app/features/tier3_*.py` into Stage 3/4.
- Add join strategy confirmation after Stage 2.
- Store `join_quality_report`.

Acceptance criteria:
- Multi-file sessions actually use secondary file features.
- Results show whether secondary data improved the call list.

### 12. Add Intervention-Aware Output

The final product is not only prediction. It is a sales action list.

Proposed behavior:
- Group high-risk customers by likely reason and suggested intervention.
- Produce call scripts or action tags:
  - frequency drop
  - product mix change
  - service issue
  - loyalty disengagement
  - credit/payment risk
  - field-visit gap
- Estimate expected value for each customer when revenue exists.

Likely implementation:
- Extend `app/stages/s8_inference.py`.
- Add `intervention_reason` and `recommended_action` fields.
- Use SHAP plus source-tier mapping plus domain rules.

Acceptance criteria:
- Output can be handed to a field team without requiring interpretation by a data scientist.

### 13. Add Outcome Feedback Loop

The long-term SOTA version should learn from sales actions.

Proposed behavior:
- Let users upload or enter post-campaign outcomes:
  - called/not called
  - offer used
  - customer responded
  - next purchase date
  - revenue recovered
- Track which interventions worked.
- Use outcomes to improve ranking and action recommendations.

Likely implementation:
- Add `campaigns`, `interventions`, and `outcomes` tables.
- Add endpoint for outcome upload.
- Add future uplift/treatment-aware modeling path.

Acceptance criteria:
- Model quality is measured against real actions, not just historical churn labels.

## Implementation Sequence

### Phase 1: Modeling Trust Core

1. Temporal validation harness.
2. Baseline challengers.
3. Top-K call-list metrics.
4. Champion selection policy.
5. Evidence pack.

This phase changes model selection from metric picking to defensible model selection.

### Phase 2: Probability And Segment Trust

1. Calibration report and calibrated inference probabilities.
2. Segment stability diagnostics.
3. Data readiness gates.
4. LLM evaluator upgrade to consume computed evidence.

This phase makes the agent skeptical before it presents confident output.

### Phase 3: Multi-Source And Business Action

1. Real multi-file joins and tier-3 feature integration.
2. Data-source lift attribution.
3. Intervention-aware call-list output.
4. Downloadable evidence and field-team action report.

This phase turns the model into a business workflow.

### Phase 4: Learning System

1. Campaign outcome capture.
2. Intervention effectiveness tracking.
3. Treatment-aware ranking.
4. Continuous benchmark history across customer uploads.

This phase turns AutoModel from a one-shot churn predictor into a learning retention system.

## Near-Term Code Targets

Files/modules to add:
- `app/validation/backtest.py`
- `app/validation/baselines.py`
- `app/validation/topk.py`
- `app/validation/calibration.py`
- `app/validation/segments.py`
- `app/validation/data_readiness.py`
- `app/agent/champion_policy.py`
- `app/agent/evidence_pack.py`

Files/modules to modify:
- `app/agent/loop.py`
- `app/agent/evaluator.py`
- `app/agent/model_trainer.py`
- `app/stages/s3_churn_window.py`
- `app/stages/s4_features.py`
- `app/stages/s6_train.py`
- `app/stages/s7_results.py`
- `app/stages/s8_inference.py`
- `app/models/schemas.py`
- `app/db/models.py`
- `app/persistence.py`
- `static/index.html`

## Non-Negotiable Product Principle

The agent should not ask, "Which model has the best AUC?"

It should ask, "Can I prove this call list would have helped the sales team before these customers were lost?"

