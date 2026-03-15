"""Agent loop that iterates over feature engineering, training, and evaluation."""
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.agent.evaluator import evaluate, SUCCESS_CRITERIA
from app.db.engine import AsyncSessionLocal
from app.persistence import save_agent_run, save_agent_iteration, load_agent_state
from app.agent.scoring import composite_score
from app.agent.feature_dsl import execute_dsl_features
from app.agent.feature_engineer import suggest_dsl_features
from app.agent.model_trainer import ModelResult, train_all_models, prepare_data
from app.models.schemas import DSLFeature, LLMEvaluationOutput
from app.stages.s4_features import compute_feature_matrix_async
from app.stages.s5_labels import _get_churn_window
from app.stages.s3_field_analysis import analyze_all_fields
from app.stages.s4_pruning import statistical_pruning, leakage_detection

logger = logging.getLogger(__name__)


@dataclass
class IterationResult:
    """Stores results from a single agent iteration."""
    iteration: int
    features_used: list[str]
    features_removed: list[str]
    features_added: list[str]
    model_results: list[ModelResult]
    evaluation: LLMEvaluationOutput


@dataclass
class AgentState:
    """Tracks agent loop state across iterations."""
    session_id: str
    iteration: int = 0
    max_iterations: int = 5
    status: str = "running"  # running | success | completed | failed | interrupted
    history: list[IterationResult] = field(default_factory=list)
    champion: ModelResult | None = None
    excluded_features: list[str] = field(default_factory=list)
    dsl_features: list[DSLFeature] = field(default_factory=list)
    user_overrides: dict = field(default_factory=dict)
    success_criteria: dict = field(default_factory=lambda: SUCCESS_CRITERIA.copy())
    messages: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize agent state for API responses."""
        champion_dict = None
        if self.champion:
            champion_dict = {
                "name": self.champion.name,
                "metrics": self.champion.metrics,
                "confusion_matrix": self.champion.confusion_matrix,
                "feature_importance": self.champion.feature_importance,
                "training_time": self.champion.training_time,
            }

        history_dicts = []
        for h in self.history:
            model_results_dicts = []
            for mr in h.model_results:
                model_results_dicts.append({
                    "name": mr.name,
                    "metrics": mr.metrics,
                    "confusion_matrix": mr.confusion_matrix,
                    "feature_importance": mr.feature_importance,
                    "training_time": mr.training_time,
                })
            history_dicts.append({
                "iteration": h.iteration,
                "features_used": h.features_used,
                "features_removed": h.features_removed,
                "features_added": h.features_added,
                "model_results": model_results_dicts,
                "evaluation": h.evaluation.model_dump(),
            })

        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "status": self.status,
            "history": history_dicts,
            "champion": champion_dict,
        }


# Global registry for active agent states and broadcast callbacks
_agent_states: dict[str, AgentState] = {}
_broadcast_callbacks: dict[str, list] = {}


def get_agent_state(session_id: str) -> AgentState | None:
    """Return the agent state for a session or None."""
    return _agent_states.get(session_id)


def set_agent_state(session_id: str, state: AgentState):
    """Store the agent state for a session."""
    _agent_states[session_id] = state


def register_broadcast_callback(session_id: str, callback):
    """Register a callback for broadcasting progress to WebSocket clients."""
    if session_id not in _broadcast_callbacks:
        _broadcast_callbacks[session_id] = []
    _broadcast_callbacks[session_id].append(callback)


def unregister_broadcast_callback(session_id: str, callback):
    """Remove a broadcast callback for a session."""
    if session_id in _broadcast_callbacks:
        _broadcast_callbacks[session_id] = [
            cb for cb in _broadcast_callbacks[session_id] if cb is not callback
        ]


async def broadcast_progress(session_id: str, msg_type: str, data: dict):
    """Broadcast a progress message to all connected WebSocket clients."""
    callbacks = _broadcast_callbacks.get(session_id, [])
    for cb in callbacks:
        try:
            await cb(msg_type, data)
        except Exception as e:
            logger.warning(f"Broadcast callback failed: {e}")


def check_user_overrides(state: AgentState) -> dict | None:
    """Check and consume user overrides."""
    if state.user_overrides:
        overrides = state.user_overrides.copy()
        state.user_overrides = {}
        return overrides
    return None


def apply_overrides(state: AgentState, overrides: dict):
    """Apply user overrides to agent state."""
    if "remove_features" in overrides:
        for feat in overrides["remove_features"]:
            if feat not in state.excluded_features:
                state.excluded_features.append(feat)

    if "add_features" in overrides:
        for feat_dict in overrides["add_features"]:
            try:
                dsl_feat = DSLFeature(**feat_dict)
                state.dsl_features.append(dsl_feat)
            except Exception:
                pass

    if "change_criteria" in overrides:
        state.success_criteria.update(overrides["change_criteria"])

    if "stop" in overrides:
        state.status = "interrupted"

    if "skip_to_completion" in overrides:
        state.status = "completed"


def pick_best_across_iterations(history: list[IterationResult]) -> ModelResult | None:
    """Pick the model with the highest composite score across all iterations."""
    best = None
    best_score = -1
    for h in history:
        for mr in h.model_results:
            score = composite_score(mr.metrics)
            if score > best_score:
                best_score = score
                best = mr
    return best


async def run_agent(session_id: str, session: dict) -> AgentState:
    """Run the agent loop. Expects session to have completed stages 1-3."""
    state = get_agent_state(session_id)
    if state is None:
        state = AgentState(session_id=session_id)
        set_agent_state(session_id, state)

    # Extract session data
    df = session.get("dataframe")
    column_mapping = session.get("column_mapping")
    hypothesis = session.get("hypothesis")
    mcq_answers = session.get("mcq_answers", {})
    raw_col_map = session.get("col_map")

    if df is None or column_mapping is None or hypothesis is None:
        state.status = "failed"
        state.messages.append({"type": "error", "text": "Stages 1-3 must be completed first"})
        return state

    # Normalize col_map format.
    # Stage 3 stores {column_name: role} but agent loop needs {role: column_name}.
    # We keep both: col_map={role: col_name} for lookups, col_map_by_name={col_name: role} for analyze_all_fields.
    if raw_col_map is None:
        from app.stages.s4_features import _build_col_map
        col_map = _build_col_map(column_mapping)  # {role: column_name}
        col_map_by_name = {v: k for k, v in col_map.items()}
    elif "customer_id" not in raw_col_map and "customer_id" in raw_col_map.values():
        # Stage 3 format: {column_name: role} — invert it
        col_map_by_name = raw_col_map
        col_map = {role: col_name for col_name, role in raw_col_map.items()}
        logger.info("[AGENT] Inverted col_map from {col_name: role} to {role: col_name}")
    else:
        col_map = raw_col_map  # already {role: column_name}
        col_map_by_name = {v: k for k, v in col_map.items()}

    # Check if exhaustive analysis was done (new pipeline)
    has_exhaustive = session.get("field_analysis_signature") is not None
    pre_computed_features = session.get("feature_matrix") if has_exhaustive else None
    pre_computed_labels = session.get("labels") if has_exhaustive else None

    # Load user-derived DSL features from session
    user_dsl_raw = session.get("user_dsl_features", [])
    if user_dsl_raw:
        for fd in user_dsl_raw:
            try:
                dsl_feat = DSLFeature(**fd) if isinstance(fd, dict) else fd
                if dsl_feat.name not in [d.name for d in state.dsl_features]:
                    state.dsl_features.insert(0, dsl_feat)
            except Exception:
                pass

    # Use pre-computed churn window from Stage 3b if available
    churn_window_days = session.get("churn_window_days") or _get_churn_window(df, col_map, mcq_answers)

    # Time split
    date_col = col_map.get("transaction_date")
    if date_col:
        dates = pd.to_datetime(df[date_col], format="mixed", dayfirst=True)
        max_date = dates.max()
        cutoff_date = max_date - pd.Timedelta(days=churn_window_days)
        df_obs = df[dates <= cutoff_date].copy()

        if len(df_obs) == 0:
            state.status = "failed"
            state.messages.append({"type": "error", "text": "Not enough data before cutoff date"})
            return state
    else:
        # No date column — use full dataset (pre-aggregated data)
        df_obs = df.copy()
        cutoff_date = None

    # Use pre-computed labels from Stage 3b, or compute from scratch
    if pre_computed_labels is not None:
        labels = pre_computed_labels
    elif date_col and cutoff_date is not None:
        from app.stages.s5_labels import _assign_labels
        cust_col = col_map["customer_id"]
        labels = _assign_labels(df, col_map, cutoff_date)
    else:
        # No date column and no pre-computed labels — cannot proceed
        state.status = "failed"
        state.messages.append({"type": "error", "text": "No transaction dates found and no pre-computed labels. Cannot determine churn."})
        return state

    # Recompute feature matrix on observation-period data to prevent temporal leakage.
    # Stage 3 computed features on the FULL dataset (including churn window).
    # We must recompute using only df_obs (data before cutoff).
    if pre_computed_features is not None and date_col and cutoff_date is not None:
        customer_id_col = col_map.get("customer_id")
        if customer_id_col:
            logger.info("[AGENT] Recomputing features on observation data (cutoff=%s)", cutoff_date.date())
            await broadcast_progress(session_id, "agent_progress", {
                "iteration": 0, "status": "recomputing_features",
                "detail": "Recomputing features on observation window...",
            })
            _, pre_computed_features = analyze_all_fields(
                df_obs, col_map_by_name, customer_id_col, date_col, labels=None,
            )
            session["feature_matrix"] = pre_computed_features

    # If exhaustive analysis exists, run pruning and leakage detection once
    if pre_computed_features is not None and state.iteration == 0:
        await broadcast_progress(session_id, "agent_progress", {
            "iteration": 0, "status": "pruning",
            "detail": "Running statistical pruning and leakage detection...",
        })
        pre_computed_features, pruning_report = statistical_pruning(pre_computed_features, labels)
        pre_computed_features, leakage_report = leakage_detection(pre_computed_features, labels, col_map)
        session["feature_matrix"] = pre_computed_features
        session["pruning_report"] = pruning_report
        session["leakage_report"] = leakage_report

    # Give WebSocket time to register broadcast callback
    await asyncio.sleep(0.5)

    await broadcast_progress(session_id, "agent_progress", {
        "iteration": 0, "status": "starting", "detail": "Agent loop starting..."
    })

    while state.iteration < state.max_iterations and state.status == "running":
        state.iteration += 1
        logger.info(f"[AGENT] Iteration {state.iteration} STARTING")
        prev_features = (
            state.history[-1].features_used if state.history else []
        )

        await broadcast_progress(session_id, "agent_progress", {
            "iteration": state.iteration,
            "status": "computing_features",
            "detail": f"Iteration {state.iteration}: Computing features...",
        })

        # 1. Compute features
        try:
            if pre_computed_features is not None:
                # Use pre-computed exhaustive features, add DSL on top
                logger.info(f"[AGENT] Iter {state.iteration}: copying pre_computed_features ({pre_computed_features.shape})")
                feature_matrix = pre_computed_features.copy()

                # Add DSL features if any
                if state.dsl_features:
                    logger.info(f"[AGENT] Iter {state.iteration}: executing {len(state.dsl_features)} DSL features")
                    dsl_matrix = execute_dsl_features(df_obs, col_map, state.dsl_features)
                    logger.info(f"[AGENT] Iter {state.iteration}: DSL features done, cols={len(dsl_matrix.columns) if dsl_matrix is not None else 0}")
                    if dsl_matrix is not None and len(dsl_matrix.columns) > 0:
                        feature_matrix = feature_matrix.join(dsl_matrix, how="left")

                # Remove excluded features
                exclude_cols = [f for f in state.excluded_features if f in feature_matrix.columns]
                if exclude_cols:
                    feature_matrix = feature_matrix.drop(columns=exclude_cols)

                tier1_names = list(feature_matrix.columns)
                tier2_names = []
                dsl_names = [d.name for d in state.dsl_features if d.name in feature_matrix.columns]
            else:
                feature_matrix, tier1_names, tier2_names, dsl_names = await compute_feature_matrix_async(
                    df_obs, col_map, column_mapping, hypothesis, mcq_answers,
                    excluded_features=state.excluded_features,
                    dsl_features=state.dsl_features,
                )
        except Exception as e:
            logger.error(f"Feature computation failed: {e}")
            state.status = "failed"
            state.messages.append({"type": "error", "text": f"Feature computation failed: {e}"})
            break

        all_features = tier1_names + tier2_names + dsl_names

        if len(feature_matrix.columns) == 0:
            state.status = "failed"
            state.messages.append({"type": "error", "text": "No features computed"})
            break

        # 2. Align labels with feature matrix
        common_idx = feature_matrix.index.intersection(labels.index)
        if len(common_idx) < 10:
            state.status = "failed"
            state.messages.append({"type": "error", "text": "Too few labeled samples"})
            break

        fm_aligned = feature_matrix.loc[common_idx]
        labels_aligned = labels.loc[common_idx]

        # Check for sufficient class balance
        n_pos = labels_aligned.sum()
        n_neg = len(labels_aligned) - n_pos
        if n_pos < 2 or n_neg < 2:
            state.status = "failed"
            state.messages.append({"type": "error", "text": "Insufficient class balance for training"})
            break

        await broadcast_progress(session_id, "agent_progress", {
            "iteration": state.iteration,
            "status": "training",
            "detail": f"Iteration {state.iteration}: Training XGBoost + Random Forest...",
        })

        # 3. Train all models
        try:
            logger.info(f"[AGENT] Iter {state.iteration}: prepare_data ({fm_aligned.shape})")
            X_train, X_test, y_train, y_test, feature_names = prepare_data(fm_aligned, labels_aligned)
            logger.info(f"[AGENT] Iter {state.iteration}: training models ({X_train.shape[1]} features)")
            model_results = train_all_models(X_train, X_test, y_train, y_test, feature_names)
            logger.info(f"[AGENT] Iter {state.iteration}: training done, {len(model_results)} models")
        except Exception as e:
            logger.error(f"Training failed: {e}")
            state.messages.append({"type": "error", "text": f"Training failed: {e}"})
            # Continue to next iteration if possible
            state.history.append(IterationResult(
                iteration=state.iteration,
                features_used=all_features,
                features_removed=[],
                features_added=[],
                model_results=[],
                evaluation=LLMEvaluationOutput(
                    leakage_detected=False, suspect_features=[],
                    leakage_reasoning="Training failed",
                    quality_acceptable=False, best_model="",
                    suggested_adjustments=["Retry with different features"],
                    reasoning="Training failed",
                ),
            ))
            continue

        if not model_results:
            state.messages.append({"type": "error", "text": "No models trained"})
            continue

        await broadcast_progress(session_id, "agent_progress", {
            "iteration": state.iteration,
            "status": "evaluating",
            "detail": f"Iteration {state.iteration}: Evaluating models...",
        })

        # 4. Evaluate — build feature definitions for leakage detection
        from app.stages.s4_features import FEATURE_DEFINITIONS
        feature_defs = {}
        for f in all_features:
            if f in FEATURE_DEFINITIONS:
                feature_defs[f] = FEATURE_DEFINITIONS[f]
            else:
                # Check DSL features for description
                dsl_desc = next(
                    (d.description for d in state.dsl_features if d.name == f),
                    f,
                )
                feature_defs[f] = dsl_desc
        history_dicts = [
            {
                "iteration": h.iteration,
                "features_removed": h.features_removed,
                "features_added": h.features_added,
            }
            for h in state.history
        ]
        if cutoff_date is not None:
            churn_label_info = f"Churn window: {churn_window_days} days. Customer is churned if no purchase after cutoff date ({cutoff_date.date()})."
        else:
            churn_label_info = f"Churn window: {churn_window_days} days. Labels were pre-computed from field analysis."

        logger.info(f"[AGENT] Iter {state.iteration}: calling LLM evaluate")
        evaluation = await evaluate(
            model_results,
            feature_definitions=feature_defs,
            churn_label_info=churn_label_info,
            iteration_history=history_dicts,
            criteria=state.success_criteria,
        )
        logger.info(f"[AGENT] Iter {state.iteration}: evaluate done. quality={evaluation.quality_acceptable}, leakage={evaluation.leakage_detected}")

        # Determine added/removed features
        features_added = [f for f in all_features if f not in prev_features]
        features_removed = [f for f in prev_features if f not in all_features]

        # 5. Record iteration
        iteration_result = IterationResult(
            iteration=state.iteration,
            features_used=all_features,
            features_removed=features_removed,
            features_added=features_added,
            model_results=model_results,
            evaluation=evaluation,
        )
        state.history.append(iteration_result)

        # 6. Broadcast iteration results
        await broadcast_progress(session_id, "iteration_result", {
            "iteration": state.iteration,
            "models": [
                {"name": mr.name, "metrics": mr.metrics}
                for mr in model_results
            ],
            "evaluation": evaluation.model_dump(),
            "features_used": all_features,
        })

        # 6a. After iteration 1, publish early results so user sees output immediately
        if state.iteration == 1 and model_results:
            early_best = max(model_results, key=lambda mr: composite_score(mr.metrics))
            # Update in-memory session only (no DB persist) to avoid blocking event loop
            from app.session_store import store as _store
            early_metrics = {**early_best.metrics, "champion_name": early_best.name}
            _session = _store.get(session_id)
            if _session:
                _session.update({
                    "model": early_best.model,
                    "feature_names": early_best.feature_names or feature_names,
                    "X_test": X_test,
                    "y_test": y_test,
                    "metrics": early_metrics,
                    "feature_importance": early_best.feature_importance[:10],
                    "confusion_matrix_data": early_best.confusion_matrix,
                    "training_time_seconds": early_best.training_time,
                    "feature_matrix": fm_aligned,
                    "labeled_features": fm_aligned,
                    "labels": labels_aligned,
                    "col_map": col_map,
                    "stage": 6,
                    "status": "results",
                })
            await broadcast_progress(session_id, "early_results_ready", {
                "champion": {
                    "name": early_best.name,
                    "metrics": early_best.metrics,
                    "feature_importance": early_best.feature_importance[:10],
                },
                "iteration": 1,
                "max_iterations": state.max_iterations,
            })

        # 6a-2. For iterations 2+, check if this iteration's best model beats previous best
        if state.iteration > 1 and model_results:
            iter_best = max(model_results, key=lambda mr: composite_score(mr.metrics))
            prev_best = pick_best_across_iterations(state.history[:-1])
            prev_score = composite_score(prev_best.metrics) if prev_best else 0
            new_score = composite_score(iter_best.metrics)

            if new_score > prev_score:
                # Update in-memory session only (no DB persist) to avoid blocking event loop
                from app.session_store import store as _store
                improved_metrics = {**iter_best.metrics, "champion_name": iter_best.name}
                _session = _store.get(session_id)
                if _session:
                    _session.update({
                        "model": iter_best.model,
                        "feature_names": iter_best.feature_names or feature_names,
                        "X_test": X_test,
                        "y_test": y_test,
                        "metrics": improved_metrics,
                        "feature_importance": iter_best.feature_importance[:10],
                        "confusion_matrix_data": iter_best.confusion_matrix,
                        "training_time_seconds": iter_best.training_time,
                        "feature_matrix": fm_aligned,
                        "labeled_features": fm_aligned,
                        "labels": labels_aligned,
                        "col_map": col_map,
                    })
                await broadcast_progress(session_id, "results_improved", {
                    "champion": {
                        "name": iter_best.name,
                        "metrics": iter_best.metrics,
                        "feature_importance": iter_best.feature_importance[:10],
                    },
                    "iteration": state.iteration,
                    "max_iterations": state.max_iterations,
                    "improvement": round(new_score - prev_score, 4),
                })

        # 6b. Persist iteration to DB
        try:
            async with AsyncSessionLocal() as db:
                # Ensure agent_run row exists
                run_dict = {
                    "status": state.status,
                    "iteration": state.iteration,
                    "max_iterations": state.max_iterations,
                    "excluded_features": state.excluded_features,
                    "success_criteria": state.success_criteria,
                }
                agent_run_id = await save_agent_run(db, session_id, run_dict)
                iter_dict = {
                    "iteration": iteration_result.iteration,
                    "features_used": iteration_result.features_used,
                    "features_removed": iteration_result.features_removed,
                    "features_added": iteration_result.features_added,
                    "model_results": [
                        {
                            "name": mr.name,
                            "metrics": mr.metrics,
                            "feature_importance": mr.feature_importance,
                            "confusion_matrix": mr.confusion_matrix,
                            "training_time": mr.training_time,
                        }
                        for mr in iteration_result.model_results
                    ],
                    "evaluation": iteration_result.evaluation.model_dump(),
                }
                await save_agent_iteration(db, agent_run_id, iter_dict)
        except Exception as e:
            logger.warning(f"Failed to persist iteration {state.iteration}: {e}")

        # Check user overrides
        overrides = check_user_overrides(state)
        if overrides:
            apply_overrides(state, overrides)
            if state.status != "running":
                break
            await broadcast_progress(session_id, "agent_response", {
                "text": f"Applied user overrides: {list(overrides.keys())}"
            })

        # 7. Check success
        if evaluation.quality_acceptable and not evaluation.leakage_detected:
            # Select champion based on LLM recommendation
            champion = None
            for mr in model_results:
                if mr.name == evaluation.best_model:
                    champion = mr
                    break
            if champion is None:
                champion = max(model_results, key=lambda mr: composite_score(mr.metrics))

            state.champion = champion
            state.status = "success"

            # Store model in session for inference
            from app.session_store import store
            metrics_with_name = {**champion.metrics, "champion_name": champion.name}
            store.update(session_id, {
                "model": champion.model,
                "feature_names": champion.feature_names or feature_names,
                "X_test": X_test,
                "y_test": y_test,
                "metrics": metrics_with_name,
                "feature_importance": champion.feature_importance[:10],
                "confusion_matrix_data": champion.confusion_matrix,
                "training_time_seconds": champion.training_time,
                "feature_matrix": fm_aligned,
                "labeled_features": fm_aligned,
                "labels": labels_aligned,
                "col_map": col_map,
                "stage": 6,
                "status": "results",
            })

            await broadcast_progress(session_id, "champion_selected", {
                "champion": {
                    "name": champion.name,
                    "metrics": champion.metrics,
                    "feature_importance": champion.feature_importance[:10],
                },
                "iterations_taken": state.iteration,
                "all_models": [
                    {"name": mr.name, "metrics": mr.metrics}
                    for mr in model_results
                ],
            })
            break

        # 8. Apply adjustments from evaluation
        for feat in evaluation.suspect_features:
            if feat not in state.excluded_features:
                state.excluded_features.append(feat)
                await broadcast_progress(session_id, "agent_response", {
                    "text": f"Removed suspect feature: {feat}"
                })

        # 9. Suggest new DSL features if more iterations remain
        if state.iteration < state.max_iterations:
            await broadcast_progress(session_id, "agent_progress", {
                "iteration": state.iteration,
                "status": "suggesting_features",
                "detail": "Asking LLM for new feature ideas...",
            })

            best_metrics = model_results[0].metrics if model_results else None
            data_profile = session.get("profile", {})

            logger.info(f"[AGENT] Iter {state.iteration}: calling LLM suggest_dsl_features")
            new_features = await suggest_dsl_features(
                data_profile=data_profile,
                col_map=col_map,
                hypothesis=hypothesis,
                existing_features=all_features,
                iteration_metrics=best_metrics,
                excluded_features=state.excluded_features,
            )
            logger.info(f"[AGENT] Iter {state.iteration}: suggest_dsl_features done, got {len(new_features)} features")

            for nf in new_features:
                state.dsl_features.append(nf)

            if new_features:
                await broadcast_progress(session_id, "agent_response", {
                    "text": f"Added {len(new_features)} new features: {[f.name for f in new_features]}"
                })

    # If loop ended without success, pick the best model across all iterations
    if state.status == "running":
        state.champion = pick_best_across_iterations(state.history)
        state.status = "completed"

        if state.champion:
            from app.session_store import store
            metrics_with_name = {**state.champion.metrics, "champion_name": state.champion.name}
            store.update(session_id, {
                "model": state.champion.model,
                "feature_names": state.champion.feature_names or feature_names,
                "X_test": X_test,
                "y_test": y_test,
                "metrics": metrics_with_name,
                "feature_importance": state.champion.feature_importance[:10],
                "confusion_matrix_data": state.champion.confusion_matrix,
                "training_time_seconds": state.champion.training_time,
                "feature_matrix": fm_aligned,
                "labeled_features": fm_aligned,
                "labels": labels_aligned,
                "col_map": col_map,
                "stage": 6,
                "status": "results",
            })

            await broadcast_progress(session_id, "champion_selected", {
                "champion": {
                    "name": state.champion.name,
                    "metrics": state.champion.metrics,
                    "feature_importance": state.champion.feature_importance[:10],
                },
                "iterations_taken": state.iteration,
                "status": "completed_max_iterations",
            })

    # Persist final agent run state to DB
    try:
        champion_dict = None
        if state.champion:
            champion_dict = {
                "name": state.champion.name,
                "metrics": state.champion.metrics,
                "feature_importance": state.champion.feature_importance[:10],
                "confusion_matrix": state.champion.confusion_matrix,
                "training_time": state.champion.training_time,
            }
        async with AsyncSessionLocal() as db:
            await save_agent_run(db, session_id, {
                "status": state.status,
                "iteration": state.iteration,
                "max_iterations": state.max_iterations,
                "excluded_features": state.excluded_features,
                "success_criteria": state.success_criteria,
                "champion": champion_dict,
            })
    except Exception as e:
        logger.warning(f"Failed to persist final agent run: {e}")

    set_agent_state(session_id, state)
    return state
