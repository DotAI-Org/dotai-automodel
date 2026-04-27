# Backend Index

*Auto-generated from source code. Do not edit the auto-generated sections.*

## API Routes

| Method | Path | Handler | File |
|--------|------|---------|------|
| GET | `/api/sessions` | `list_sessions()` | `app/main.py` |
| POST | `/api/sessions` | `create_session()` | `app/main.py` |
| POST | `/api/sessions/multi` | `create_session_multi()` | `app/main.py` |
| DELETE | `/api/sessions/{session_id}` | `delete_session()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/agent/start` | `start_agent()` | `app/main.py` |
| GET | `/api/sessions/{session_id}/agent/status` | `agent_status()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/agent/stop` | `stop_agent()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/column-mapping` | `column_mapping()` | `app/main.py` |
| PUT | `/api/sessions/{session_id}/column-mapping` | `override_column_mapping()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/column-mapping/feedback` | `column_mapping_feedback()` | `app/main.py` |
| GET | `/api/sessions/{session_id}/cross-file-summary` | `cross_file_summary()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/features` | `features()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/findings/confirm` | `confirm_findings()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/findings/correct` | `correct_findings()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/hypothesis` | `hypothesis()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/inference` | `inference()` | `app/main.py` |
| GET | `/api/sessions/{session_id}/inference/download` | `inference_download()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/labels` | `labels()` | `app/main.py` |
| PUT | `/api/sessions/{session_id}/name` | `rename_session()` | `app/main.py` |
| GET | `/api/sessions/{session_id}/results` | `results()` | `app/main.py` |
| POST | `/api/sessions/{session_id}/train` | `train()` | `app/main.py` |
| GET | `/auth/google` | `login_google()` | `app/auth/router.py` |
| GET | `/auth/google/callback` | `auth_google_callback()` | `app/auth/router.py` |
| GET | `/auth/me` | `me()` | `app/auth/router.py` |
| GET | `/health` | `health()` | `app/main.py` |
| WEBSOCKET | `/sessions/{session_id}/chat` | `chat_websocket()` | `app/chat/router.py` |

## `app/`

### `main.py`
> FastAPI application entry point and route definitions.

- `async health()` `@app.get('/health')` (line 73)
  > Return health check status.
- `async get_session_with_auth(session_id, user)` (line 89)
  > Load session, verify ownership.
- `async list_sessions(user)` `@api_router.get('/sessions')` (line 106)
  > Return all sessions for the authenticated user.
- `async rename_session(session_id, body, user)` `@api_router.put('/sessions/{session_id}/name')` (line 112)
  > Rename a session by ID.
- `async delete_session(session_id, user)` `@api_router.delete('/sessions/{session_id}')` (line 120)
  > Delete a session by ID.
- `async create_session(file, user)` `@api_router.post('/sessions')` (line 130)
  > Upload a CSV file and create a new session.
- `async create_session_multi(files, description, file_metadata, user)` `@api_router.post('/sessions/multi')` (line 149)
  > Upload multiple CSV files with per-file type metadata.
- `async column_mapping(session_id, user)` `@api_router.post('/sessions/{session_id}/column-mapping')` (line 176)
  > Run LLM-based column role detection for a session.
- `async override_column_mapping(session_id, body, user)` `@api_router.put('/sessions/{session_id}/column-mapping')` (line 183)
  > Override column mappings with user-provided values.
- `async column_mapping_feedback(session_id, body, user)` `@api_router.post('/sessions/{session_id}/column-mapping/feedback')` (line 190)
  > Re-run column mapping with user feedback.
- `async hypothesis(session_id, body, user)` `@api_router.post('/sessions/{session_id}/hypothesis')` (line 199)
  > Generate business hypothesis and MCQ questions for a session.
- `async confirm_findings(session_id, body, user)` `@api_router.post('/sessions/{session_id}/findings/confirm')` (line 207)
  > User confirms computed findings — proceed to training.
- `async correct_findings(session_id, body, user)` `@api_router.post('/sessions/{session_id}/findings/correct')` (line 218)
  > User overrides findings via MCQ answers.
- `async cross_file_summary(session_id, user)` `@api_router.get('/sessions/{session_id}/cross-file-summary')` (line 228)
  > Get detected data types and cross-file summary.
- `async features(session_id, body, user)` `@api_router.post('/sessions/{session_id}/features')` (line 240)
  > Compute feature matrix using MCQ answers.
- `async labels(session_id, user)` `@api_router.post('/sessions/{session_id}/labels')` (line 249)
  > Assign churn labels based on cutoff date.
- `async train(session_id, user)` `@api_router.post('/sessions/{session_id}/train')` (line 258)
  > Train an XGBoost model on labeled features.
- `async results(session_id, user)` `@api_router.get('/sessions/{session_id}/results')` (line 267)
  > Return model results with LLM-generated summary.
- `async inference(session_id, user)` `@api_router.post('/sessions/{session_id}/inference')` (line 276)
  > Run churn predictions on all customers.
- `async inference_download(session_id, user)` `@api_router.get('/sessions/{session_id}/inference/download')` (line 283)
  > Download churn predictions as a CSV file.
- `async start_agent(session_id, background_tasks, user)` `@api_router.post('/sessions/{session_id}/agent/start')` (line 297)
  > Start the agent loop as a background task.
- `async agent_status(session_id, user)` `@api_router.get('/sessions/{session_id}/agent/status')` (line 326)
  > Return the agent loop status for a session.
- `async stop_agent(session_id, user)` `@api_router.post('/sessions/{session_id}/agent/stop')` (line 365)
  > Signal the agent loop to stop.
- `async startup()` `@app.on_event('startup')` (line 382)
  > Initialize database and set engine on session store.

  **Calls to other modules:**
  - `get_session_with_auth` → `fastapi.HTTPException`
  - `get_session_with_auth` → `app.session_store.store.get`
  - `get_session_with_auth` → `app.session_store.store.get_or_load`
  - `get_session_with_auth` → `app.session_store.store.get_owner`
  - `list_sessions` → `fastapi.Depends`
  - `list_sessions` → `app.session_store.store.list_sessions`
  - `rename_session` → `fastapi.Depends`
  - `rename_session` → `app.session_store.store.rename`
  - `delete_session` → `fastapi.Depends`
  - `delete_session` → `app.session_store.store.delete`
  - `create_session` → `fastapi.Depends`
  - `create_session` → `fastapi.File`
  - `create_session` → `app.notifications.notify_gchat`
  - `create_session` → `app.stages.s1_upload.handle`
  - `create_session_multi` → `fastapi.Depends`
  - `create_session_multi` → `fastapi.File`
  - `create_session_multi` → `fastapi.Form`
  - `create_session_multi` → `app.notifications.notify_gchat`
  - `create_session_multi` → `app.stages.s1_upload.handle_multi`
  - `column_mapping` → `fastapi.Depends`
  - `column_mapping` → `app.stages.s2_column_map.handle`
  - `override_column_mapping` → `fastapi.Depends`
  - `override_column_mapping` → `app.stages.s2_column_map.handle_override`
  - `column_mapping_feedback` → `fastapi.Depends`
  - `column_mapping_feedback` → `app.stages.s2_column_map.handle_with_feedback`
  - `hypothesis` → `fastapi.Depends`
  - `hypothesis` → `app.stages.s3_hypothesis.handle`
  - `confirm_findings` → `fastapi.Depends`
  - `confirm_findings` → `app.session_store.store.update`
  - `correct_findings` → `fastapi.Depends`
  - `correct_findings` → `app.session_store.store.update`
  - `cross_file_summary` → `fastapi.Depends`
  - `features` → `fastapi.Depends`
  - `features` → `app.stages.s4_features.handle`
  - `labels` → `fastapi.Depends`
  - `labels` → `app.stages.s5_labels.handle`
  - `train` → `fastapi.Depends`
  - `train` → `app.stages.s6_train.handle`
  - `results` → `fastapi.Depends`
  - `results` → `app.stages.s7_results.handle`
  - `inference` → `fastapi.Depends`
  - `inference` → `app.stages.s8_inference.handle`
  - `inference_download` → `fastapi.Depends`
  - `inference_download` → `fastapi.responses.StreamingResponse`
  - `inference_download` → `app.stages.s8_inference.handle_download`
  - `start_agent` → `app.agent.loop.AgentState`
  - `start_agent` → `fastapi.Depends`
  - `start_agent` → `fastapi.HTTPException`
  - `start_agent` → `app.agent.loop.get_agent_state`
  - `start_agent` → `logging.logging.getLogger`
  - `start_agent` → `logging.logging.getLogger(__name__).error`
  - `start_agent` → `app.notifications.notify_gchat`
  - `start_agent` → `app.agent.loop.run_agent`
  - `start_agent` → `app.agent.loop.set_agent_state`
  - `start_agent` → `app.session_store.store.get`
  - `agent_status` → `app.db.engine.AsyncSessionLocal`
  - `agent_status` → `fastapi.Depends`
  - `agent_status` → `fastapi.HTTPException`
  - `agent_status` → `app.agent.loop.get_agent_state`
  - `agent_status` → `app.persistence.load_agent_state`
  - `stop_agent` → `fastapi.Depends`
  - `stop_agent` → `fastapi.HTTPException`
  - `stop_agent` → `app.agent.loop.get_agent_state`
  - `startup` → `app.db.engine.init_db`
  - `startup` → `app.session_store.store.set_engine`

### `notifications.py`
> Google Chat webhook notification sender.

- `_get_webhook_url()` (line 13)
  > Return the cached webhook URL from environment.
- `async notify_gchat(title, detail)` (line 21)
  > Post an alert to Google Chat. No-ops if webhook URL is unset.
- `fire_and_forget(title, detail)` (line 39)
  > Schedule notify_gchat as a background task. Safe to call from anywhere.

  **Calls to other modules:**
  - `_get_webhook_url` → `os.os.environ.get`
  - `notify_gchat` → `httpx.httpx.AsyncClient`
  - `fire_and_forget` → `asyncio.asyncio.get_running_loop`

### `persistence.py`
> Session and pipeline state persistence to PostgreSQL.

- `serialize_blob(obj)` (line 45)
  > Compress and pickle an object to bytes.
- `deserialize_blob(data)` (line 50)
  > Decompress and unpickle bytes to an object.
- `session_dict_to_db_columns(session_dict)` (line 55)
  > Convert an in-memory session dict to DB column values.
- `db_row_to_session_dict(row)` (line 69)
  > Convert a DB row back to the in-memory session dict format.
- `async save_session(db, session_id, session_dict)` (line 99)
  > Upsert session data to DB.
- `async load_session(db, session_id)` (line 117)
  > Load session from DB and return as in-memory dict.
- `async save_chat_message(db, session_id, role, content, metadata)` (line 126)
  > Persist a chat message.
- `async save_agent_run(db, session_id, agent_state_dict)` (line 138)
  > Upsert an AgentRun row. Returns the agent_run.id.
- `async save_agent_iteration(db, agent_run_id, iteration_dict)` (line 177)
  > Insert an AgentIteration row.
- `async load_agent_state(db, session_id)` (line 202)
  > Load latest AgentRun + AgentIterations and return dict matching AgentState.to_dict() shape.
- `async load_chat_history(db, session_id)` (line 242)
  > Load chat history for a session.

  **Calls to other modules:**
  - `serialize_blob` → `pickle.pickle.dumps`
  - `serialize_blob` → `zlib.zlib.compress`
  - `deserialize_blob` → `pickle.pickle.loads`
  - `deserialize_blob` → `zlib.zlib.decompress`
  - `save_session` → `sqlalchemy.select`
  - `load_session` → `sqlalchemy.select`
  - `save_chat_message` → `app.db.models.ChatMessage`
  - `save_agent_run` → `app.db.models.AgentRun`
  - `save_agent_run` → `app.db.models.AgentRun.created_at.desc`
  - `save_agent_run` → `sqlalchemy.select`
  - `save_agent_iteration` → `app.db.models.AgentIteration`
  - `load_agent_state` → `app.db.models.AgentRun.created_at.desc`
  - `load_agent_state` → `sqlalchemy.select`
  - `load_chat_history` → `sqlalchemy.select`

### `session_store.py`
> In-memory session store with database persistence.

- **class `SessionStore`** (line 13)
  > Manages in-memory session cache with database persistence.
  - `__init__(self)`
  - `set_engine(self, engine)`
    > Set the SQLAlchemy engine for database operations.
  - `async create(self, user_id)`
    > Create a new session in database and cache, return session ID.
  - `get(self, session_id)`
    > Return session data from cache or None.
  - `async get_or_load(self, session_id)`
    > Check cache first, fall back to DB.
  - `update(self, session_id, data)`
    > Update session data in cache and schedule database persistence.
  - `async _persist(self, session_id)`
    > Write session data to database.
  - `async delete(self, session_id)`
    > Remove session from cache and database.
  - `async list_sessions(self, user_id)`
    > Return all sessions for a user from database.
  - `async rename(self, session_id, name)`
    > Update session name in database and cache.
  - `async get_owner(self, session_id)`
    > Get the user_id that owns this session.

  **Calls to other modules:**
  - `SessionStore.create` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.create` → `app.db.models.Session`
  - `SessionStore.create` → `uuid.uuid.uuid4`
  - `SessionStore.get_or_load` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.get_or_load` → `app.persistence.load_session`
  - `SessionStore.update` → `asyncio.asyncio.ensure_future`
  - `SessionStore._persist` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore._persist` → `app.persistence.save_session`
  - `SessionStore.delete` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.delete` → `sqlalchemy.delete`
  - `SessionStore.list_sessions` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.list_sessions` → `app.db.models.Session.updated_at.desc`
  - `SessionStore.list_sessions` → `sqlalchemy.select`
  - `SessionStore.rename` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.rename` → `sqlalchemy.select`
  - `SessionStore.get_owner` → `app.db.engine.AsyncSessionLocal`
  - `SessionStore.get_owner` → `sqlalchemy.select`

## `app/agent/`

### `evaluator.py`
> LLM-based model evaluation with rule checks for leakage and quality.

- `check_rules(model_results, criteria)` (line 20)
  > Rule-based checks against success criteria. Returns dict with pass/fail and details.
- `async evaluate(model_results, feature_definitions, churn_label_info, iteration_history, criteria)` (line 69)
  > Evaluate model results using rule-based checks + LLM judgment.

  **Calls to other modules:**
  - `check_rules` → `app.agent.scoring.composite_score`
  - `evaluate` → `app.models.schemas.LLMEvaluationOutput`
  - `evaluate` → `app.agent.scoring.composite_score`
  - `evaluate` → `app.llm.client.generate_structured`

### `feature_dsl.py`
> DSL feature execution engine for per-customer aggregations.

- `execute_dsl_feature(df, col_map, feature_def)` (line 11)
  > Execute a single DSL feature definition and return a Series indexed by customer_id.
- `execute_dsl_features(df, col_map, feature_defs, excluded)` (line 38)
  > Execute multiple DSL feature definitions. Returns DataFrame indexed by customer_id.
- `_resolve_column(col_map, col_ref)` (line 62)
  > Resolve a column reference. If it matches a role in col_map, return the mapped name. Otherwise return as-is.
- `_op_aggregate(df, col_map, cust_col, params)` (line 67)
  > Compute per-customer aggregation on a column.
- `_op_aggregate_window(df, col_map, cust_col, params)` (line 75)
  > Compute per-customer aggregation within a time window.
- `_op_ratio(df, col_map, cust_col, params)` (line 96)
  > Compute ratio of two per-customer aggregations.
- `_op_trend(df, col_map, cust_col, params)` (line 143)
  > Compute first-half vs second-half difference for a column.
- `_op_conditional_count(df, col_map, cust_col, params)` (line 174)
  > Count rows per customer matching a condition.
- `_op_nunique(df, col_map, cust_col, params)` (line 216)
  > Count distinct values per customer for a column.
- `_op_gap_stat(df, col_map, cust_col, params)` (line 222)
  > Compute a statistic on inter-purchase gaps per customer.
- `_apply_agg_func(grouped, func)` (line 248)
  > Apply a named aggregation function to a grouped object.

  **Calls to other modules:**
  - `execute_dsl_features` → `pandas.pd.DataFrame`
  - `_op_aggregate_window` → `pandas.pd.Series`
  - `_op_aggregate_window` → `pandas.pd.Timedelta`
  - `_op_aggregate_window` → `pandas.pd.to_datetime`
  - `_op_ratio` → `pandas.pd.Series`
  - `_op_ratio` → `pandas.pd.Timedelta`
  - `_op_ratio` → `pandas.pd.to_datetime`
  - `_op_trend` → `pandas.pd.Series`
  - `_op_trend` → `pandas.pd.to_datetime`
  - `_op_gap_stat` → `pandas.pd.to_datetime`
  - `_op_gap_stat` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`

### `feature_engineer.py`
> LLM-based DSL feature suggestion for the agent loop.

- `async suggest_dsl_features(data_profile, col_map, hypothesis, existing_features, iteration_metrics, excluded_features)` (line 36)
  > Ask the LLM to suggest new DSL features based on context.

  **Calls to other modules:**
  - `suggest_dsl_features` → `app.llm.client.generate_structured`

### `loop.py`
> Agent loop that iterates over feature engineering, training, and evaluation.

- **class `IterationResult`** (line 26)
  > Stores results from a single agent iteration.
- **class `AgentState`** (line 37)
  > Tracks agent loop state across iterations.
  - `to_dict(self)`
    > Serialize agent state for API responses.
- `get_agent_state(session_id)` (line 98)
  > Return the agent state for a session or None.
- `set_agent_state(session_id, state)` (line 103)
  > Store the agent state for a session.
- `register_broadcast_callback(session_id, callback)` (line 108)
  > Register a callback for broadcasting progress to WebSocket clients.
- `unregister_broadcast_callback(session_id, callback)` (line 115)
  > Remove a broadcast callback for a session.
- `async broadcast_progress(session_id, msg_type, data)` (line 123)
  > Broadcast a progress message to all connected WebSocket clients.
- `check_user_overrides(state)` (line 133)
  > Check and consume user overrides.
- `apply_overrides(state, overrides)` (line 142)
  > Apply user overrides to agent state.
- `pick_best_across_iterations(history)` (line 167)
  > Pick the model with the highest composite score across all iterations.
- `async run_agent(session_id, session)` (line 180)
  > Run the agent loop. Expects session to have completed stages 1-3.

  **Calls to other modules:**
  - `apply_overrides` → `app.models.schemas.DSLFeature`
  - `pick_best_across_iterations` → `app.agent.scoring.composite_score`
  - `run_agent` → `app.db.engine.AsyncSessionLocal`
  - `run_agent` → `app.models.schemas.DSLFeature`
  - `run_agent` → `app.models.schemas.LLMEvaluationOutput`
  - `run_agent` → `app.stages.s5_labels._assign_labels`
  - `run_agent` → `app.stages.s4_features._build_col_map`
  - `run_agent` → `app.stages.s5_labels._get_churn_window`
  - `run_agent` → `app.session_store._store.get`
  - `run_agent` → `app.stages.s3_field_analysis.analyze_all_fields`
  - `run_agent` → `asyncio.asyncio.sleep`
  - `run_agent` → `app.agent.scoring.composite_score`
  - `run_agent` → `app.stages.s4_features.compute_feature_matrix_async`
  - `run_agent` → `app.agent.evaluator.evaluate`
  - `run_agent` → `app.agent.feature_dsl.execute_dsl_features`
  - `run_agent` → `app.stages.s4_pruning.leakage_detection`
  - `run_agent` → `pandas.pd.Timedelta`
  - `run_agent` → `pandas.pd.to_datetime`
  - `run_agent` → `app.agent.model_trainer.prepare_data`
  - `run_agent` → `app.persistence.save_agent_iteration`
  - `run_agent` → `app.persistence.save_agent_run`
  - `run_agent` → `app.stages.s4_pruning.statistical_pruning`
  - `run_agent` → `app.session_store.store.update`
  - `run_agent` → `app.agent.feature_engineer.suggest_dsl_features`
  - `run_agent` → `app.agent.model_trainer.train_all_models`

### `model_trainer.py`
> Multi-model training for XGBoost and Random Forest.

- **class `ModelResult`** (line 24)
  > Holds a trained model with its metrics and feature importance.
- `prepare_data(feature_matrix, labels, test_size, random_state)` (line 35)
  > Clean features and split into train/test. Returns X_train, X_test, y_train, y_test, feature_names.
- `_evaluate_model(model, X_test, y_test, feature_names)` (line 63)
  > Compute metrics, confusion matrix, and feature importance for a fitted model.
- `_train_xgboost(X_train, y_train, X_test, y_test, feature_names)` (line 95)
  > Train an XGBoost classifier and return its ModelResult.
- `_train_random_forest(X_train, y_train, X_test, y_test, feature_names)` (line 127)
  > Train a Random Forest classifier and return its ModelResult.
- `train_all_models(X_train, X_test, y_train, y_test, feature_names)` (line 153)
  > Train XGBoost and Random Forest on the same split. Returns list sorted by AUC descending.

  **Calls to other modules:**
  - `prepare_data` → `sklearn.model_selection.train_test_split`
  - `_evaluate_model` → `sklearn.metrics.confusion_matrix`
  - `_evaluate_model` → `sklearn.metrics.f1_score`
  - `_evaluate_model` → `sklearn.metrics.precision_score`
  - `_evaluate_model` → `sklearn.metrics.recall_score`
  - `_evaluate_model` → `sklearn.metrics.roc_auc_score`
  - `_train_xgboost` → `time.time.time`
  - `_train_xgboost` → `xgboost.xgb.XGBClassifier`
  - `_train_random_forest` → `sklearn.ensemble.RandomForestClassifier`
  - `_train_random_forest` → `time.time.time`
  - `train_all_models` → `app.agent.scoring.composite_score`

### `scoring.py`
> Composite scoring function for model comparison.

- `composite_score(metrics)` (line 4)
  > Compute a weighted score from AUC, F1, precision, and recall.

## `app/auth/`

### `config.py`
> OAuth and JWT configuration constants.


### `dependencies.py`
> JWT creation, decoding, and request authentication.

- `create_jwt(user_id, email, name)` (line 11)
  > Create a signed JWT token for a user.
- `decode_jwt(token)` (line 22)
  > Decode a JWT token and return user info dict.
- `async get_current_user(authorization)` (line 35)
  > Extract and decode JWT, verify user exists in DB.
- `get_ws_user(token)` (line 53)
  > Decode JWT from WebSocket query param.

  **Calls to other modules:**
  - `create_jwt` → `datetime.datetime.now`
  - `create_jwt` → `jose.jwt.encode`
  - `create_jwt` → `datetime.timedelta`
  - `decode_jwt` → `fastapi.HTTPException`
  - `decode_jwt` → `jose.jwt.decode`
  - `get_current_user` → `app.db.engine.AsyncSessionLocal`
  - `get_current_user` → `fastapi.HTTPException`
  - `get_current_user` → `fastapi.Header`
  - `get_current_user` → `sqlalchemy.select`

### `router.py`
> Google OAuth login and callback routes.

- `async login_google(request)` `@router.get('/google')` (line 28)
  > Redirect user to Google OAuth consent screen.
- `async auth_google_callback(request)` `@router.get('/google/callback')` (line 35)
  > Handle Google OAuth callback, create or update user, issue JWT.
- `async me(user)` `@router.get('/me')` (line 80)
  > Return the authenticated user's profile.

  **Calls to other modules:**
  - `auth_google_callback` → `app.db.engine.AsyncSessionLocal`
  - `auth_google_callback` → `fastapi.responses.RedirectResponse`
  - `auth_google_callback` → `app.db.models.User`
  - `auth_google_callback` → `app.auth.dependencies.create_jwt`
  - `auth_google_callback` → `app.notifications.notify`
  - `auth_google_callback` → `os.os.environ.get`
  - `auth_google_callback` → `sqlalchemy.select`
  - `me` → `app.db.engine.AsyncSessionLocal`
  - `me` → `fastapi.Depends`
  - `me` → `sqlalchemy.select`

## `app/chat/`

### `handler.py`
> Chat message handler with LLM-based intent classification.

- `async handle_message(session_id, text, agent_state)` (line 12)
  > Process a user chat message and return a response + any commands.
- `_build_state_summary(state)` (line 71)
  > Build a text summary of the agent state for the LLM prompt.
- `_apply_command(state, command, params)` (line 96)
  > Apply a parsed command to the agent state via user_overrides.

  **Calls to other modules:**
  - `handle_message` → `app.llm.client.generate_structured`

### `router.py`
> WebSocket chat endpoint for agent communication.

- `async chat_websocket(websocket, session_id, token)` `@router.websocket('/sessions/{session_id}/chat')` (line 25)
  > Handle WebSocket connection for chat with the agent.

  **Calls to other modules:**
  - `chat_websocket` → `app.db.engine.AsyncSessionLocal`
  - `chat_websocket` → `fastapi.Query`
  - `chat_websocket` → `app.agent.loop.get_agent_state`
  - `chat_websocket` → `app.auth.dependencies.get_ws_user`
  - `chat_websocket` → `app.chat.handler.handle_message`
  - `chat_websocket` → `json.json.loads`
  - `chat_websocket` → `app.persistence.load_chat_history`
  - `chat_websocket` → `app.notifications.notify`
  - `chat_websocket` → `app.agent.loop.register_broadcast_callback`
  - `chat_websocket` → `app.persistence.save_chat_message`
  - `chat_websocket` → `app.session_store.store.get`
  - `chat_websocket` → `app.session_store.store.get_or_load`
  - `chat_websocket` → `app.session_store.store.get_owner`
  - `chat_websocket` → `app.agent.loop.unregister_broadcast_callback`

## `app/db/`

### `engine.py`
> SQLAlchemy async engine and session factory setup.

- `async get_db()` (line 22)
  > Yield a database session for dependency injection.
- `async init_db()` (line 28)
  > Create tables and add any missing columns from model definitions.

  **Calls to other modules:**
  - `init_db` → `app.db.models.Base.metadata.tables.items`
  - `init_db` → `sqlalchemy.sa_inspect`
  - `init_db` → `sqlalchemy.text`

### `models.py`
> SQLAlchemy ORM models for users, sessions, agent runs, and chat.

- **class `Base(DeclarativeBase)`** (line 13)
  > Base class for all ORM models.
- **class `User(Base)`** (line 23)
  > Stores user account data from OAuth providers.
- **class `Session(Base)`** (line 38)
  > Stores pipeline session state and data blobs.
- **class `SessionFile(Base)`** (line 106)
  > Stores per-file data for multi-file uploads.
- **class `AgentRun(Base)`** (line 122)
  > Stores agent loop run state and champion model.
- **class `AgentIteration(Base)`** (line 143)
  > Stores per-iteration results within an agent run.
- **class `ChatMessage(Base)`** (line 159)
  > Stores chat messages between user and agent.
- `utcnow()` (line 18)
  > Return the current UTC datetime.

  **Calls to other modules:**
  - `utcnow` → `datetime.datetime.now`

## `app/features/`

### `tier3_field.py`
> Tier 3 field interaction features.

Computes per-customer field visit features: visit frequency, duration,
order conversion, coverage.

- `compute_field_features(df, col_map, customer_id_col)` (line 10)
  > Compute field interaction features grouped by customer.

Expected roles in col_map: visit_id, visit_date, entity_type,
visit_duration, order_booked, objective.
- `_find_col(col_map, role)` (line 105)
- `_compute_gap_mean(group, date_col)` (line 112)
- `_compute_gap_std(group, date_col)` (line 122)
- `_compute_trend(series)` (line 132)

  **Calls to other modules:**
  - `compute_field_features` → `pandas.pd.DataFrame`
  - `compute_field_features` → `pandas.pd.Timedelta`
  - `compute_field_features` → `pandas.pd.to_datetime`
  - `compute_field_features` → `pandas.pd.to_numeric`
  - `compute_field_features` → `pandas.pd.to_numeric(df[order_col], errors='coerce').fillna`
  - `_compute_gap_mean` → `pandas.pd.to_datetime`
  - `_compute_gap_mean` → `pandas.pd.to_datetime(group[date_col]).sort_values`
  - `_compute_gap_std` → `pandas.pd.to_datetime`
  - `_compute_gap_std` → `pandas.pd.to_datetime(group[date_col]).sort_values`
  - `_compute_trend` → `numpy.np.arange`
  - `_compute_trend` → `numpy.np.polyfit`

### `tier3_loyalty.py`
> Tier 3 loyalty/membership features.

Computes per-customer loyalty features from loyalty program data:
points activity, tier status, engagement patterns.

- `compute_loyalty_features(df, col_map, customer_id_col)` (line 10)
  > Compute loyalty features grouped by customer.

Expected roles in col_map: points_earned, points_redeemed, tier,
enrollment_date, transaction_type, member_id.
- `_find_col(col_map, role)` (line 82)
  > Find column name for a given role.
- `_compute_trend(series)` (line 90)
  > Compute linear trend slope, normalized.

  **Calls to other modules:**
  - `compute_loyalty_features` → `pandas.pd.DataFrame`
  - `compute_loyalty_features` → `pandas.pd.to_datetime`
  - `_compute_trend` → `numpy.np.arange`
  - `_compute_trend` → `numpy.np.polyfit`

### `tier3_master.py`
> Tier 3 master data features.

Computes static features from dealer/customer master data:
tenure, credit, territory, status.

- `compute_master_features(df, col_map, customer_id_col)` (line 10)
  > Compute master data features.

Master data is typically one row per customer.
Expected roles: dealer_code, dealer_name, registration_date,
status, credit_limit, territory.
- `_find_col(col_map, role)` (line 65)

  **Calls to other modules:**
  - `compute_master_features` → `pandas.pd.DataFrame`
  - `compute_master_features` → `pandas.pd.to_datetime`
  - `compute_master_features` → `pandas.pd.to_numeric`

### `tier3_returns.py`
> Tier 3 returns/delivery features.

Computes per-customer returns features: return frequency, reasons, patterns.

- `compute_returns_features(df, col_map, customer_id_col)` (line 9)
  > Compute returns features grouped by customer.

Expected roles in col_map: return_id, return_date, return_reason,
return_quantity, original_invoice.
- `_find_col(col_map, role)` (line 77)
- `_compute_gap_mean(group, date_col)` (line 84)
- `_compute_trend(series)` (line 95)

  **Calls to other modules:**
  - `compute_returns_features` → `pandas.pd.DataFrame`
  - `compute_returns_features` → `pandas.pd.to_datetime`
  - `_compute_gap_mean` → `pandas.pd.to_datetime`
  - `_compute_gap_mean` → `pandas.pd.to_datetime(group[date_col]).sort_values`
  - `_compute_trend` → `numpy.np.arange`
  - `_compute_trend` → `numpy.np.polyfit`

### `tier3_service.py`
> Tier 3 service/warranty features.

Computes per-customer service features from service/complaint data:
ticket frequency, resolution time, satisfaction scores.

- `compute_service_features(df, col_map, customer_id_col)` (line 10)
  > Compute service features grouped by customer.

Expected roles in col_map: ticket_id, ticket_date, resolution_date,
complaint_category, warranty_status, csat_score, tat_days.
- `_find_col(col_map, role)` (line 99)
  > Find column name for a given role.
- `_compute_trend(series)` (line 107)
  > Compute linear trend slope, normalized.

  **Calls to other modules:**
  - `compute_service_features` → `pandas.pd.DataFrame`
  - `compute_service_features` → `pandas.pd.to_datetime`
  - `_compute_trend` → `numpy.np.arange`
  - `_compute_trend` → `numpy.np.polyfit`

## `app/llm/`

### `client.py`
> LLM client with Groq and Gemini providers for structured output.

- `get_reasoning_model()` (line 26)
  > Return the reasoning model name for the active provider.
- `_get_provider()` (line 32)
  > Detect and cache the LLM provider from environment variables.
- `_get_client()` (line 48)
  > Initialize and cache the LLM client instance.
- `_schema_to_json_instruction(schema)` (line 64)
  > Convert a Pydantic schema to a JSON string for LLM instructions.
- `_is_rate_limit_error(e)` (line 69)
  > Check if an exception indicates a rate limit error.
- `async generate_structured(prompt, response_schema, model, temperature)` (line 75)
  > Send a prompt to the LLM and return a validated Pydantic object.

  **Calls to other modules:**
  - `_get_provider` → `os.os.environ.get`
  - `_get_provider` → `os.os.environ.get('LLM_PROVIDER', '').lower`
  - `_get_client` → `groq.Groq`
  - `_get_client` → `google.genai.Client`
  - `_schema_to_json_instruction` → `json.json.dumps`
  - `generate_structured` → `asyncio.asyncio.sleep`
  - `generate_structured` → `json.json.loads`
  - `generate_structured` → `app.notifications.notify`
  - `generate_structured` → `os.os.environ.get`
  - `generate_structured` → `google.genai.types.GenerateContentConfig`

## `app/models/`

### `schemas.py`
> Pydantic schemas for API requests, responses, and LLM outputs.

- **class `FileType(str, Enum)`** (line 9)
  > User-declared file type for multi-file upload.
- **class `ColumnRole(str, Enum)`** (line 20)
  > Column semantic roles for mapping.
- **class `RiskTier(str, Enum)`** (line 117)
  > Churn risk classification tiers.
- **class `ColumnProfile(BaseModel)`** (line 126)
  > Profile statistics for a single column.
- **class `DataProfile(BaseModel)`** (line 135)
  > Profile statistics for an uploaded dataset.
- **class `UploadResponse(BaseModel)`** (line 143)
  > Response for single file upload.
- **class `FileProfile(BaseModel)`** (line 149)
  > Profile for a single file in a multi-file upload.
- **class `FileMetadata(BaseModel)`** (line 157)
  > Per-file metadata from the upload form.
- **class `MultiUploadResponse(BaseModel)`** (line 165)
  > Response for multi-file upload.
- **class `ColumnMapping(BaseModel)`** (line 173)
  > Maps a column name to its detected role.
- **class `ColumnMappingResponse(BaseModel)`** (line 181)
  > Response containing column-to-role mappings.
- **class `ColumnMappingOverride(BaseModel)`** (line 186)
  > Request to override column mappings.
- **class `ColumnMappingFeedback(BaseModel)`** (line 191)
  > Request to re-map columns with user feedback.
- **class `JoinStep(BaseModel)`** (line 197)
  > Describes a single join operation between two files.
- **class `LLMJoinStrategy(BaseModel)`** (line 206)
  > LLM output for multi-file join strategy.
- **class `MCQOption(BaseModel)`** (line 214)
  > A single option in a multiple choice question.
- **class `MCQuestion(BaseModel)`** (line 220)
  > A multiple choice question for business context.
- **class `BusinessHypothesis(BaseModel)`** (line 228)
  > LLM-generated business type hypothesis.
- **class `HypothesisRequest(BaseModel)`** (line 235)
  > Request body for hypothesis generation.
- **class `HypothesisResponse(BaseModel)`** (line 240)
  > Response containing hypothesis and MCQ questions.
- **class `Finding(BaseModel)`** (line 250)
  > A single data finding with churn signal strength.
- **class `FindingsResponse(BaseModel)`** (line 258)
  > Computed findings shown to user for confirmation.
- **class `FindingsConfirmRequest(BaseModel)`** (line 268)
  > User confirms or provides context to findings.
- **class `MCQAnswers(BaseModel)`** (line 276)
  > User answers to MCQ questions.
- **class `FeatureStat(BaseModel)`** (line 281)
  > Statistics for a single computed feature.
- **class `FeaturesResponse(BaseModel)`** (line 289)
  > Response containing computed features and statistics.
- **class `LabelsResponse(BaseModel)`** (line 302)
  > Response containing churn label statistics.
- **class `ConfusionMatrix(BaseModel)`** (line 313)
  > Confusion matrix counts.
- **class `FeatureImportance(BaseModel)`** (line 321)
  > Feature name with its importance score.
- **class `TrainResponse(BaseModel)`** (line 327)
  > Response containing training metrics and feature importance.
- **class `SamplePrediction(BaseModel)`** (line 341)
  > A single customer prediction with risk tier.
- **class `ResultsResponse(BaseModel)`** (line 349)
  > Response containing model results summary and predictions.
- **class `FeatureContribution(BaseModel)`** (line 363)
  > SHAP-based feature contribution for a prediction.
- **class `InferencePrediction(BaseModel)`** (line 371)
  > A single customer inference prediction with feature contributions.
- **class `InferenceResponse(BaseModel)`** (line 380)
  > Response containing inference predictions for all customers.
- **class `LLMColumnMappingItem(BaseModel)`** (line 391)
  > LLM output for a single column mapping.
- **class `LLMColumnMappingOutput(BaseModel)`** (line 398)
  > LLM output for column mapping.
- **class `LLMMCQOption(BaseModel)`** (line 403)
  > LLM output for a MCQ option.
- **class `LLMMCQ(BaseModel)`** (line 409)
  > LLM output for a MCQ question.
- **class `LLMHypothesisOutput(BaseModel)`** (line 417)
  > LLM output for business hypothesis generation.
- **class `LLMFeatureSelectionOutput(BaseModel)`** (line 425)
  > LLM output for tier 2 feature selection.
- **class `LLMResultsSummaryOutput(BaseModel)`** (line 431)
  > LLM output for results summary text.
- **class `DSLFeature(BaseModel)`** (line 438)
  > Definition of a DSL-based feature with operation and parameters.
  - `params(self)` `@property`
    > Parse params_json string into a dict.
- **class `LLMFeatureSuggestionOutput(BaseModel)`** (line 452)
  > LLM output for DSL feature suggestions.
- **class `LLMEvaluationOutput(BaseModel)`** (line 458)
  > LLM output for model evaluation with leakage detection.
- **class `LLMChatOutput(BaseModel)`** (line 469)
  > LLM output for chat message classification.
- **class `ModelResultSchema(BaseModel)`** (line 477)
  > Schema for serialized model results in API responses.
- **class `IterationResultSchema(BaseModel)`** (line 486)
  > Schema for a single agent iteration result.
- **class `AgentStatusResponse(BaseModel)`** (line 498)
  > Response for agent loop status.
- **class `SessionListItem(BaseModel)`** (line 510)
  > Schema for a session in the session list.
- **class `RenameRequest(BaseModel)`** (line 522)
  > Request body for renaming a session.
- **class `UserInfo(BaseModel)`** (line 527)
  > Schema for user profile information.
- `get_roles_for_file_type(file_type)` (line 106)
  > Return applicable column roles for a given file type.

  **Calls to other modules:**
  - `DSLFeature.params` → `json.json.loads`

## `app/stages/`

### `s1_upload.py`
> Stage 1: CSV file upload, parsing, and profiling.

- `async handle_multi(files, description, file_metadata_json, user_id)` (line 22)
  > Parse and profile multiple uploaded CSV files with per-file type metadata.
- `_validate_file_type(df, profile, file_type)` (line 124)
  > Return warnings if declared file_type does not match data.
- `_detect_data_types(file_types)` (line 158)
  > Map file_type tags to data type numbers (1-5).
- `async handle(file, user_id)` (line 168)
  > Parse and profile a single uploaded CSV file.
- `_build_profile(df)` (line 200)
  > Build a DataProfile from a DataFrame.
- `_infer_dtype(series)` (line 245)
  > Infer the semantic data type of a pandas Series.

  **Calls to other modules:**
  - `handle_multi` → `app.models.schemas.FileProfile`
  - `handle_multi` → `fastapi.HTTPException`
  - `handle_multi` → `app.models.schemas.MultiUploadResponse`
  - `handle_multi` → `io.io.BytesIO`
  - `handle_multi` → `json.json.loads`
  - `handle_multi` → `pandas.pd.read_csv`
  - `handle_multi` → `app.session_store.store.create`
  - `handle_multi` → `app.session_store.store.update`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.UploadResponse`
  - `handle` → `io.io.BytesIO`
  - `handle` → `pandas.pd.read_csv`
  - `handle` → `app.session_store.store.create`
  - `handle` → `app.session_store.store.update`
  - `_build_profile` → `app.models.schemas.ColumnProfile`
  - `_build_profile` → `app.models.schemas.DataProfile`
  - `_build_profile` → `pandas.pd.to_datetime`
  - `_infer_dtype` → `pandas.pd.api.types.is_datetime64_any_dtype`
  - `_infer_dtype` → `pandas.pd.api.types.is_numeric_dtype`
  - `_infer_dtype` → `pandas.pd.to_datetime`

### `s2_column_map.py`
> Stage 2: LLM-based column role detection and multi-file joining.

- `async handle(session_id, session)` (line 23)
  > Run LLM column mapping on the session profile.

For multi-file sessions, maps each file with its file_type context.
- `async _handle_multi(session_id, session, dataframes)` (line 66)
  > Map columns for each file with its file_type context, then produce cross-file summary.
- `_detect_data_types_from_files(dataframes)` (line 123)
  > Map file_type tags to Type 1-5.
- `_build_cross_file_summary(dataframes, all_mappings, detected_types)` (line 134)
  > Build a human-readable summary of detected types and file relationships.
- `handle_override(session_id, session, body)` (line 157)
  > Replace column mappings with user-provided overrides.
- `async handle_with_feedback(session_id, session, body)` (line 169)
  > Re-run LLM column mapping with user feedback.
- `_build_prompt(profile, file_description, file_type)` (line 217)
  > Build the LLM prompt for column role detection, type-aware.
- `_get_role_descriptions(roles)` (line 303)
  > Format role descriptions for the LLM prompt.
- `async join_files(session_id, session)` (line 312)
  > Join multiple uploaded files into a single DataFrame using LLM-determined strategy.

Returns a dict with 'dataframe', 'join_summary' keys.
If session has a single file or already has a dataframe, returns it directly.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.ColumnMapping`
  - `handle` → `app.models.schemas.ColumnMappingResponse`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.llm.client.generate_structured`
  - `handle` → `app.session_store.store.update`
  - `_handle_multi` → `app.models.schemas.ColumnMapping`
  - `_handle_multi` → `app.models.schemas.ColumnMappingResponse`
  - `_handle_multi` → `app.llm.client.generate_structured`
  - `_handle_multi` → `app.session_store.store.update`
  - `handle_override` → `app.models.schemas.ColumnMappingResponse`
  - `handle_override` → `app.session_store.store.update`
  - `handle_with_feedback` → `app.models.schemas.ColumnMapping`
  - `handle_with_feedback` → `app.models.schemas.ColumnMappingResponse`
  - `handle_with_feedback` → `fastapi.HTTPException`
  - `handle_with_feedback` → `app.llm.client.generate_structured`
  - `handle_with_feedback` → `app.session_store.store.update`
  - `_build_prompt` → `app.models.schemas.get_roles_for_file_type`
  - `join_files` → `fastapi.HTTPException`
  - `join_files` → `app.llm.client.generate_structured`
  - `join_files` → `pandas.pd.merge`
  - `join_files` → `app.session_store.store.update`

### `s3_churn_window.py`
> Auto churn window selection.

Tests 6 candidate windows (30, 60, 90, 120, 180, 365 days),
trains a fast XGBoost for each, picks the one with best F1.

- `auto_select_churn_window(df, feature_matrix, customer_id_col, date_col)` (line 16)
  > Test 6 churn windows, return the one with best F1.

Args:
    df: raw DataFrame
    feature_matrix: pre-computed per-customer features from field analysis
    customer_id_col: name of customer ID column
    date_col: name of transaction date column

Returns:
    {
        "selected_window": int,
        "all_results": list of per-window results,
        "adaptive_gap": pd.Series (gap_vs_personal_median per customer),
    }
- `generate_labels(df, customer_id_col, date_col, window)` (line 105)
  > Generate binary churn labels for a given window.

Returns:
    pd.Series indexed by customer_id, values 0 (active) or 1 (churned).
- `_train_fast_xgb(X, y)` (line 123)
  > Train a fast XGBoost and return F1 score.
- `_compute_adaptive_gap(df, customer_id_col, date_col, max_date)` (line 156)
  > Compute gap_vs_personal_median per customer.

Value of 2.5 means the customer has been silent for 2.5x their normal interval.

  **Calls to other modules:**
  - `auto_select_churn_window` → `pandas.pd.Timedelta`
  - `auto_select_churn_window` → `pandas.pd.to_datetime`
  - `generate_labels` → `pandas.pd.Timedelta`
  - `generate_labels` → `pandas.pd.to_datetime`
  - `_train_fast_xgb` → `sklearn.metrics.f1_score`
  - `_train_fast_xgb` → `sklearn.model_selection.train_test_split`
  - `_train_fast_xgb` → `xgboost.xgb.XGBClassifier`
  - `_compute_adaptive_gap` → `pandas.pd.to_datetime`

### `s3_field_analysis.py`
> Exhaustive field analysis engine.

Runs 4 analyses per field based on dtype (numeric, categorical, datetime).
One pass produces both the data signature report (for LLM hypothesis)
and the per-customer feature matrix (for training).

- `analyze_all_fields(df, col_map, customer_id_col, date_col, labels)` (line 15)
  > Run 4 analyses per field based on dtype.

Args:
    df: raw DataFrame
    col_map: {column_name: role} mapping from Stage 2
    customer_id_col: name of the customer ID column
    date_col: name of the primary date column (for trend computation)
    labels: optional churn labels (for univariate signal analysis)

Returns:
    signature: dict of per-field statistics
    feature_matrix: DataFrame indexed by customer_id
- `analyze_numeric(df, col_name, customer_id_col, date_col, labels)` (line 86)
  > 4 analyses for a numeric field.

1. Distribution (signature only)
2. Per-customer profile (signature + features)
3. Univariate churn signal (signature only)
4. Temporal trend (feature)
- `analyze_categorical(df, col_name, customer_id_col, date_col, labels)` (line 146)
  > 4 analyses for a categorical field.

1. Concentration (signature only)
2. Per-customer diversity (feature)
3. Churn rate by value (feature)
4. Temporal shift (feature)
- `analyze_datetime(df, col_name, customer_id_col)` (line 205)
  > 4 analyses for a datetime field.

1. Recency (feature)
2. Frequency (feature)
3. Gap profile (feature)
4. Seasonality (signature only)
- `analyze_cross_file(df_primary, df_secondary, primary_customer_col, secondary_customer_col, secondary_file_type)` (line 276)
  > Compute cross-file overlap statistics.
- `_is_auto_increment(series)` (line 303)
  > Detect auto-incrementing integer columns (row IDs, transaction IDs, etc.).

Handles both per-row unique IDs and transaction-level IDs that repeat
across line items. Checks deduplicated values for: numeric, integer-valued,
and mostly monotonically increasing (>90% of consecutive diffs are positive).
- `_infer_analysis_dtype(series)` (line 330)
  > Determine dtype for analysis purposes.
- `_safe_float(val)` (line 348)
  > Convert to float, return 0.0 on failure.
- `_compute_univariate_auc(feature_series, labels)` (line 359)
  > Compute univariate AUC of a feature against binary labels.
- `_compute_trend(df, col_name, customer_id_col, date_col, numeric_col)` (line 376)
  > Compute 2nd half mean minus 1st half mean per customer.
- `_compute_categorical_shift(df, col_name, customer_id_col, date_col)` (line 407)
  > Compute Jaccard distance of value sets between 1st and 2nd half per customer.
- `_compute_gap_profile(df_valid, col_name, customer_id_col)` (line 439)
  > Compute inter-event gap statistics per customer.

  **Calls to other modules:**
  - `analyze_all_fields` → `pandas.pd.DataFrame`
  - `analyze_numeric` → `numpy.np.abs`
  - `analyze_numeric` → `pandas.pd.to_numeric`
  - `analyze_datetime` → `pandas.pd.Series`
  - `analyze_datetime` → `pandas.pd.Timedelta`
  - `analyze_datetime` → `pandas.pd.to_datetime`
  - `_is_auto_increment` → `numpy.np.allclose`
  - `_is_auto_increment` → `pandas.pd.api.types.is_numeric_dtype`
  - `_infer_analysis_dtype` → `pandas.pd.api.types.is_datetime64_any_dtype`
  - `_infer_analysis_dtype` → `pandas.pd.api.types.is_numeric_dtype`
  - `_infer_analysis_dtype` → `pandas.pd.to_datetime`
  - `_safe_float` → `numpy.np.isinf`
  - `_safe_float` → `numpy.np.isnan`
  - `_compute_univariate_auc` → `numpy.np.unique`
  - `_compute_univariate_auc` → `sklearn.metrics.roc_auc_score`
  - `_compute_trend` → `pandas.pd.to_datetime`
  - `_compute_trend` → `pandas.pd.to_numeric`
  - `_compute_categorical_shift` → `pandas.pd.to_datetime`
  - `_compute_gap_profile` → `pandas.pd.Series`

### `s3_hypothesis.py`
> Stage 3: Exhaustive field analysis, auto churn window, grounded hypothesis.

Revised flow:
  3a. Exhaustive field analysis (4 analyses per dtype on every field)
  3b. Auto-select churn window (test 6 candidates)
  3c. LLM hypothesis grounded in computed facts
  3d. Generate findings for user confirmation
  3e. MCQs with defaults (shown only on "Let me correct")

- `async handle(session_id, session, free_text)` (line 32)
  > Run exhaustive field analysis, auto churn window, grounded hypothesis.
- `_get_col(col_map, role)` (line 158)
  > Find the column name assigned to a given role.
- `_recompute_univariate_aucs(signature, feature_matrix, labels)` (line 166)
  > Recompute univariate AUCs with the auto-selected churn window labels.
- `_generate_findings(signature, churn_window_result)` (line 193)
  > Build the findings object shown to the user.
- `_build_grounded_prompt(signature, churn_window_result, profile, free_text)` (line 251)
  > Build LLM prompt grounded in computed facts from field analysis.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.BusinessHypothesis`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.HypothesisResponse`
  - `handle` → `app.models.schemas.MCQOption`
  - `handle` → `app.models.schemas.MCQuestion`
  - `handle` → `app.stages.s3_field_analysis.analyze_all_fields`
  - `handle` → `app.stages.s3_churn_window.auto_select_churn_window`
  - `handle` → `app.stages.s3_churn_window.generate_labels`
  - `handle` → `app.llm.client.generate_structured`
  - `handle` → `app.llm.client.get_reasoning_model`
  - `handle` → `app.session_store.store.update`
  - `_recompute_univariate_aucs` → `app.stages.s3_field_analysis._compute_univariate_auc`

### `s4_cross_source.py`
> Cross-source feature computation.

Computes interaction features between primary and secondary data,
and between high-signal fields within the same dataset.

- `compute_cross_source_features(primary_features, secondary_features, secondary_type)` (line 14)
  > Compute interaction features between primary and secondary data.

Join on index (customer_id). Left join: primary customers as base.
- `compute_interaction_features(feature_matrix, signature)` (line 69)
  > For pairs of features with AUC > 0.60, compute ratio and product.

Limits to top 5 high-signal features to avoid combinatorial explosion.

  **Calls to other modules:**
  - `compute_cross_source_features` → `pandas.pd.DataFrame`
  - `compute_interaction_features` → `pandas.pd.DataFrame`

### `s4_features.py`
> Stage 4: Feature engineering with tier 1, tier 2, and DSL features.

- `compute_recency(df, col_map)` (line 55)
  > Compute days since each customer's last purchase.
- `compute_frequency_30d(df, col_map)` (line 66)
  > Compute transaction count per customer in the last 30 days.
- `compute_frequency_60d(df, col_map)` (line 71)
  > Compute transaction count per customer in the last 60 days.
- `compute_frequency_90d(df, col_map)` (line 76)
  > Compute transaction count per customer in the last 90 days.
- `_frequency_window(df, col_map, days)` (line 81)
  > Compute transaction count per customer within a day window.
- `compute_monetary_total(df, col_map)` (line 94)
  > Compute total transaction amount per customer.
- `compute_monetary_avg(df, col_map)` (line 99)
  > Compute average transaction amount per customer.
- `compute_frequency_trend(df, col_map)` (line 104)
  > Compute change in transaction count between first and second half.
- `compute_monetary_trend(df, col_map)` (line 123)
  > Compute change in average transaction amount between halves.
- `compute_days_between_purchases_avg(df, col_map)` (line 142)
  > Compute average days between consecutive purchases per customer.
- `compute_days_between_purchases_std(df, col_map)` (line 157)
  > Compute standard deviation of inter-purchase gaps per customer.
- `compute_basket_diversity(df, col_map)` (line 174)
  > Compute number of distinct products per customer.
- `compute_category_concentration(df, col_map)` (line 181)
  > Compute proportion of purchases in the top category per customer.
- `compute_channel_diversity(df, col_map)` (line 193)
  > Compute number of distinct channels used per customer.
- `compute_avg_basket_size(df, col_map)` (line 200)
  > Compute average quantity per transaction per customer.
- `compute_peak_vs_offpeak_ratio(df, col_map)` (line 207)
  > Compute ratio of holiday-season to off-season purchases per customer.
- `compute_order_size_trend(df, col_map)` (line 226)
  > Compute change in average order size between halves.
- `compute_product_mix_change(df, col_map)` (line 245)
  > Compute Jaccard distance of product sets between halves per customer.
- `compute_region_loyalty(df, col_map)` (line 269)
  > Compute proportion of purchases in the top region per customer.
- `compute_weekend_vs_weekday(df, col_map)` (line 281)
  > Compute ratio of weekend to weekday purchases per customer.
- `compute_repeat_product_rate(df, col_map)` (line 298)
  > Compute proportion of products purchased more than once per customer.
- `compute_max_gap_between_purchases(df, col_map)` (line 312)
  > Compute the longest gap in days between purchases per customer.
- `compute_purchase_regularity_score(df, col_map)` (line 327)
  > Compute purchase regularity score (1 minus coefficient of variation).
- `async handle(session_id, session, body)` (line 381)
  > Stage 4: receive pre-computed matrix from Stage 3, prune, detect leakage.

If exhaustive field analysis was run (Stage 3 new flow), uses that matrix.
Otherwise falls back to legacy Tier 1 + Tier 2 computation.
- `async _handle_exhaustive(session_id, session, body)` (line 397)
  > Handle Stage 4 when exhaustive field analysis has been run.
- `async _handle_legacy(session_id, session, body)` (line 457)
  > Legacy flow: compute Tier 1 + Tier 2 features from scratch.
- `_build_stats(feature_matrix)` (line 564)
  > Build feature statistics list.
- `_build_tier_map(columns, col_map, detected_types)` (line 578)
  > Map each feature to its tier based on the source column role.
- `_tier_distribution(tier_map)` (line 610)
  > Compute percentage distribution across tiers.
- `async _extract_user_features(free_text, col_map, existing_features)` (line 619)
  > Translate user free text into DSL feature definitions via LLM.
- `_build_col_map(column_mapping)` (line 666)
  > Map role -> column name from the column mapping.
- `_get_available_tier2(col_map)` (line 676)
  > Return Tier 2 feature names whose required columns exist.
- `compute_feature_matrix(df_obs, col_map, column_mapping, hypothesis, mcq_answers, excluded_features, dsl_features)` (line 685)
  > Compute features from observation window data.

Returns (feature_matrix, tier1_names, tier2_names, dsl_names).
This function is used by both the stage handler and the agent loop.
- `async compute_feature_matrix_async(df_obs, col_map, column_mapping, hypothesis, mcq_answers, excluded_features, dsl_features)` (line 770)
  > Async version of compute_feature_matrix. Used by agent loop.
- `async _select_tier2_features(available, column_mapping, hypothesis, mcq_answers)` (line 829)
  > Ask LLM to select which tier 2 features to compute.

  **Calls to other modules:**
  - `compute_recency` → `pandas.pd.to_datetime`
  - `compute_recency` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).max`
  - `_frequency_window` → `pandas.pd.Timedelta`
  - `_frequency_window` → `pandas.pd.to_datetime`
  - `compute_frequency_trend` → `pandas.pd.to_datetime`
  - `compute_monetary_trend` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_avg` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_avg` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`
  - `compute_days_between_purchases_std` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_std` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`
  - `compute_peak_vs_offpeak_ratio` → `pandas.pd.to_datetime`
  - `compute_order_size_trend` → `pandas.pd.to_datetime`
  - `compute_product_mix_change` → `pandas.pd.to_datetime`
  - `compute_weekend_vs_weekday` → `pandas.pd.to_datetime`
  - `compute_max_gap_between_purchases` → `pandas.pd.to_datetime`
  - `compute_max_gap_between_purchases` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`
  - `compute_purchase_regularity_score` → `pandas.pd.to_datetime`
  - `compute_purchase_regularity_score` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`
  - `_handle_exhaustive` → `app.models.schemas.FeaturesResponse`
  - `_handle_exhaustive` → `fastapi.HTTPException`
  - `_handle_exhaustive` → `app.stages.s4_cross_source.compute_interaction_features`
  - `_handle_exhaustive` → `app.stages.s4_pruning.leakage_detection`
  - `_handle_exhaustive` → `app.stages.s4_pruning.statistical_pruning`
  - `_handle_exhaustive` → `app.session_store.store.update`
  - `_handle_legacy` → `app.models.schemas.FeaturesResponse`
  - `_handle_legacy` → `fastapi.HTTPException`
  - `_handle_legacy` → `app.stages.s5_labels._get_churn_window`
  - `_handle_legacy` → `app.agent.feature_dsl.execute_dsl_features`
  - `_handle_legacy` → `pandas.pd.DataFrame`
  - `_handle_legacy` → `pandas.pd.Timedelta`
  - `_handle_legacy` → `pandas.pd.to_datetime`
  - `_handle_legacy` → `app.session_store.store.update`
  - `_build_stats` → `app.models.schemas.FeatureStat`
  - `_extract_user_features` → `app.llm.client.generate_structured`
  - `compute_feature_matrix` → `asyncio.asyncio.get_running_loop`
  - `compute_feature_matrix` → `asyncio.asyncio.run`
  - `compute_feature_matrix` → `app.agent.feature_dsl.execute_dsl_features`
  - `compute_feature_matrix` → `pandas.pd.DataFrame`
  - `compute_feature_matrix_async` → `app.agent.feature_dsl.execute_dsl_features`
  - `compute_feature_matrix_async` → `pandas.pd.DataFrame`
  - `_select_tier2_features` → `app.llm.client.generate_structured`

### `s4_pruning.py`
> Statistical pruning and three-layer leakage detection.

Pruning: removes zero-variance, high-null, and correlated features.
Leakage detection: statistical (AUC >0.90), temporal ordering, ablation test.

- `statistical_pruning(feature_matrix, labels)` (line 14)
  > Remove noise features.

Steps:
1. Drop zero-variance features
2. Drop features with >90% null
3. Drop correlated features (|r| > 0.95, keep higher AUC)

Returns:
    Pruned feature matrix, pruning report.
- `leakage_detection(feature_matrix, labels, col_map)` (line 86)
  > Three-layer leakage detection.

Layer 1: Statistical — flag features with univariate AUC > 0.90
Layer 2: Temporal ordering — check if recency/frequency features
Layer 3: Ablation test — train with/without suspect feature

Returns:
    Cleaned feature matrix, leakage report.
- `_safe_auc(feature, labels)` (line 190)
  > Compute univariate AUC, return 0.5 on failure.
- `_ablation_test(X, labels, feature_name)` (line 205)
  > Train model with and without a feature, measure AUC drop.

  **Calls to other modules:**
  - `statistical_pruning` → `numpy.np.ones`
  - `statistical_pruning` → `numpy.np.triu`
  - `statistical_pruning` → `numpy.np.triu(np.ones(corr.shape), k=1).astype`
  - `_safe_auc` → `numpy.np.unique`
  - `_safe_auc` → `sklearn.metrics.roc_auc_score`
  - `_ablation_test` → `sklearn.metrics.roc_auc_score`
  - `_ablation_test` → `sklearn.model_selection.train_test_split`
  - `_ablation_test` → `xgboost.xgb.XGBClassifier`

### `s5_labels.py`
> Stage 5: Churn label assignment based on cutoff date.

- `handle(session_id, session)` (line 10)
  > Assign churn labels and return label statistics.

If labels were auto-selected in Stage 3b, validates and uses those.
Otherwise computes from scratch (legacy flow).
- `_extract_window_override(mcq_answers)` (line 102)
  > Extract churn window override from MCQ answers.
- `_assign_labels(df, col_map, cutoff_date)` (line 115)
  > Assign churn labels: 1 if no purchase after cutoff, 0 otherwise.
- `_get_churn_window(df, col_map, mcq_answers)` (line 135)
  > Determine churn window in days from MCQ answers or auto-derive from data.

  **Calls to other modules:**
  - `handle` → `fastapi.HTTPException`
  - `handle` → `pandas.pd.Series`
  - `handle` → `pandas.pd.Timedelta`
  - `handle` → `pandas.pd.to_datetime`
  - `handle` → `app.session_store.store.update`
  - `_assign_labels` → `pandas.pd.Series`
  - `_assign_labels` → `pandas.pd.to_datetime`
  - `_get_churn_window` → `pandas.pd.to_datetime`
  - `_get_churn_window` → `pandas.pd.to_datetime(g[date_col], format='mixed', dayfirst=True).sort_values`

### `s6_train.py`
> Stage 6: Multi-model training with tier-based feature grouping.

- `handle(session_id, session)` (line 29)
  > Train Model A (baseline) + Model B (enriched) + applicable C/D/E.
- `_handle_legacy(session_id, session, features, labels)` (line 182)
  > Legacy single-model training path.
- `_train_single(X, y, name)` (line 275)
  > Train a single XGBoost model with the given features and labels.
- `_compute_tier_attribution(champion, tier_map)` (line 363)
  > Group feature importance by tier.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.ConfusionMatrix`
  - `handle` → `app.models.schemas.FeatureImportance`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.TrainResponse`
  - `handle` → `app.session_store.store.update`
  - `handle` → `time.time.time`
  - `_handle_legacy` → `app.models.schemas.ConfusionMatrix`
  - `_handle_legacy` → `app.models.schemas.FeatureImportance`
  - `_handle_legacy` → `fastapi.HTTPException`
  - `_handle_legacy` → `app.models.schemas.TrainResponse`
  - `_handle_legacy` → `sklearn.metrics.confusion_matrix`
  - `_handle_legacy` → `sklearn.metrics.f1_score`
  - `_handle_legacy` → `sklearn.metrics.precision_score`
  - `_handle_legacy` → `sklearn.metrics.recall_score`
  - `_handle_legacy` → `sklearn.metrics.roc_auc_score`
  - `_handle_legacy` → `app.session_store.store.update`
  - `_handle_legacy` → `time.time.time`
  - `_handle_legacy` → `sklearn.model_selection.train_test_split`
  - `_handle_legacy` → `xgboost.xgb.XGBClassifier`
  - `_train_single` → `sklearn.metrics.confusion_matrix`
  - `_train_single` → `sklearn.metrics.f1_score`
  - `_train_single` → `sklearn.metrics.precision_score`
  - `_train_single` → `sklearn.metrics.recall_score`
  - `_train_single` → `sklearn.metrics.roc_auc_score`
  - `_train_single` → `sklearn.model_selection.train_test_split`
  - `_train_single` → `xgboost.xgb.XGBClassifier`

### `s7_results.py`
> Stage 7: Model results summary with LLM-generated text.

- `async handle(session_id, session)` (line 22)
  > Build results response with sample predictions and LLM summary.
- `_build_legacy_predictions(model, X_test, y_test)` (line 108)
  > Build sample predictions for legacy single-model path.
- `_build_sample_predictions(model, X_test, y_test, tier_map)` (line 126)
  > Build sample predictions with SHAP-based multi-source context.
- `async _generate_enriched_summary(metrics, feature_importance, lift, tier_attribution, leakage_report, detected_types, findings, hypothesis)` (line 156)
  > Generate summary enriched with multi-source context.
- `_get_risk_tier(probability)` (line 232)
  > Map a churn probability to a risk tier.
- `async _generate_summary(metrics, feature_importance, business_type)` (line 241)
  > Generate a text summary of model results using LLM.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.FeatureImportance`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.ResultsResponse`
  - `handle` → `app.session_store.store.update`
  - `_build_legacy_predictions` → `app.models.schemas.SamplePrediction`
  - `_build_sample_predictions` → `app.models.schemas.SamplePrediction`
  - `_build_sample_predictions` → `shap.shap.TreeExplainer`
  - `_generate_enriched_summary` → `app.llm.client.generate_structured`
  - `_generate_summary` → `app.llm.client.generate_structured`

### `s8_inference.py`
> Stage 8: Churn inference with SHAP-based feature contributions.

- `handle(session_id, session)` (line 22)
  > Run churn predictions on all customers with SHAP explanations.
- `handle_download(session_id, session)` (line 134)
  > Generate a CSV download buffer from stored predictions.
- `_get_risk_tier(probability)` (line 197)
  > Map a churn probability to a risk tier.
- `_tier_to_source(tier)` (line 206)
  > Map feature tier to data source label.
- `_generate_action(top_features, detected_types)` (line 216)
  > Generate action recommendation based on top contributing features.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.FeatureContribution`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.InferencePrediction`
  - `handle` → `app.models.schemas.InferenceResponse`
  - `handle` → `app.agent.loop.get_agent_state`
  - `handle` → `numpy.np.abs`
  - `handle` → `numpy.np.argsort`
  - `handle` → `shap.shap.TreeExplainer`
  - `handle` → `app.session_store.store.get`
  - `handle` → `app.session_store.store.update`
  - `handle_download` → `fastapi.HTTPException`
  - `handle_download` → `io.io.StringIO`
  - `handle_download` → `pandas.pd.DataFrame`
