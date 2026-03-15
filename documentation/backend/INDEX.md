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
| POST | `/api/sessions/{session_id}/features` | `features()` | `app/main.py` |
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

- `async health()` `@app.get('/health')` (line 72)
  > Return health check status.
- `async get_session_with_auth(session_id, user)` (line 88)
  > Load session, verify ownership.
- `async list_sessions(user)` `@api_router.get('/sessions')` (line 105)
  > Return all sessions for the authenticated user.
- `async rename_session(session_id, body, user)` `@api_router.put('/sessions/{session_id}/name')` (line 111)
  > Rename a session by ID.
- `async delete_session(session_id, user)` `@api_router.delete('/sessions/{session_id}')` (line 119)
  > Delete a session by ID.
- `async create_session(file, user)` `@api_router.post('/sessions')` (line 129)
  > Upload a CSV file and create a new session.
- `async create_session_multi(files, description, user)` `@api_router.post('/sessions/multi')` (line 135)
  > Upload multiple CSV files and create a new session.
- `async column_mapping(session_id, user)` `@api_router.post('/sessions/{session_id}/column-mapping')` (line 147)
  > Run LLM-based column role detection for a session.
- `async override_column_mapping(session_id, body, user)` `@api_router.put('/sessions/{session_id}/column-mapping')` (line 154)
  > Override column mappings with user-provided values.
- `async column_mapping_feedback(session_id, body, user)` `@api_router.post('/sessions/{session_id}/column-mapping/feedback')` (line 161)
  > Re-run column mapping with user feedback.
- `async hypothesis(session_id, body, user)` `@api_router.post('/sessions/{session_id}/hypothesis')` (line 170)
  > Generate business hypothesis and MCQ questions for a session.
- `async features(session_id, body, user)` `@api_router.post('/sessions/{session_id}/features')` (line 180)
  > Compute feature matrix using MCQ answers.
- `async labels(session_id, user)` `@api_router.post('/sessions/{session_id}/labels')` (line 189)
  > Assign churn labels based on cutoff date.
- `async train(session_id, user)` `@api_router.post('/sessions/{session_id}/train')` (line 198)
  > Train an XGBoost model on labeled features.
- `async results(session_id, user)` `@api_router.get('/sessions/{session_id}/results')` (line 207)
  > Return model results with LLM-generated summary.
- `async inference(session_id, user)` `@api_router.post('/sessions/{session_id}/inference')` (line 216)
  > Run churn predictions on all customers.
- `async inference_download(session_id, user)` `@api_router.get('/sessions/{session_id}/inference/download')` (line 223)
  > Download churn predictions as a CSV file.
- `async start_agent(session_id, background_tasks, user)` `@api_router.post('/sessions/{session_id}/agent/start')` (line 237)
  > Start the agent loop as a background task.
- `async agent_status(session_id, user)` `@api_router.get('/sessions/{session_id}/agent/status')` (line 266)
  > Return the agent loop status for a session.
- `async stop_agent(session_id, user)` `@api_router.post('/sessions/{session_id}/agent/stop')` (line 305)
  > Signal the agent loop to stop.
- `async startup()` `@app.on_event('startup')` (line 322)
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
  - `create_session` → `app.stages.s1_upload.handle`
  - `create_session_multi` → `fastapi.Depends`
  - `create_session_multi` → `fastapi.File`
  - `create_session_multi` → `fastapi.Form`
  - `create_session_multi` → `app.stages.s1_upload.handle_multi`
  - `column_mapping` → `fastapi.Depends`
  - `column_mapping` → `app.stages.s2_column_map.handle`
  - `override_column_mapping` → `fastapi.Depends`
  - `override_column_mapping` → `app.stages.s2_column_map.handle_override`
  - `column_mapping_feedback` → `fastapi.Depends`
  - `column_mapping_feedback` → `app.stages.s2_column_map.handle_with_feedback`
  - `hypothesis` → `fastapi.Depends`
  - `hypothesis` → `app.stages.s3_hypothesis.handle`
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
  - `_op_gap_stat` → `pandas.pd.to_datetime(g[date_col]).sort_values`

### `feature_engineer.py`
> LLM-based DSL feature suggestion for the agent loop.

- `async suggest_dsl_features(data_profile, col_map, hypothesis, existing_features, iteration_metrics, excluded_features)` (line 36)
  > Ask the LLM to suggest new DSL features based on context.

  **Calls to other modules:**
  - `suggest_dsl_features` → `app.llm.client.generate_structured`

### `loop.py`
> Agent loop that iterates over feature engineering, training, and evaluation.

- **class `IterationResult`** (line 24)
  > Stores results from a single agent iteration.
- **class `AgentState`** (line 35)
  > Tracks agent loop state across iterations.
  - `to_dict(self)`
    > Serialize agent state for API responses.
- `get_agent_state(session_id)` (line 96)
  > Return the agent state for a session or None.
- `set_agent_state(session_id, state)` (line 101)
  > Store the agent state for a session.
- `register_broadcast_callback(session_id, callback)` (line 106)
  > Register a callback for broadcasting progress to WebSocket clients.
- `unregister_broadcast_callback(session_id, callback)` (line 113)
  > Remove a broadcast callback for a session.
- `async broadcast_progress(session_id, msg_type, data)` (line 121)
  > Broadcast a progress message to all connected WebSocket clients.
- `check_user_overrides(state)` (line 131)
  > Check and consume user overrides.
- `apply_overrides(state, overrides)` (line 140)
  > Apply user overrides to agent state.
- `pick_best_across_iterations(history)` (line 165)
  > Pick the model with the highest composite score across all iterations.
- `async run_agent(session_id, session)` (line 178)
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
  - `run_agent` → `asyncio.asyncio.sleep`
  - `run_agent` → `app.agent.scoring.composite_score`
  - `run_agent` → `app.stages.s4_features.compute_feature_matrix_async`
  - `run_agent` → `app.agent.evaluator.evaluate`
  - `run_agent` → `pandas.pd.Timedelta`
  - `run_agent` → `pandas.pd.to_datetime`
  - `run_agent` → `app.agent.model_trainer.prepare_data`
  - `run_agent` → `app.persistence.save_agent_iteration`
  - `run_agent` → `app.persistence.save_agent_run`
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

- `create_jwt(user_id, email, name)` (line 10)
  > Create a signed JWT token for a user.
- `decode_jwt(token)` (line 21)
  > Decode a JWT token and return user info dict.
- `async get_current_user(authorization)` (line 34)
  > Extract and decode JWT from Authorization header.
- `get_ws_user(token)` (line 42)
  > Decode JWT from WebSocket query param.

  **Calls to other modules:**
  - `create_jwt` → `datetime.datetime.now`
  - `create_jwt` → `jose.jwt.encode`
  - `create_jwt` → `datetime.timedelta`
  - `decode_jwt` → `fastapi.HTTPException`
  - `decode_jwt` → `jose.jwt.decode`
  - `get_current_user` → `fastapi.HTTPException`
  - `get_current_user` → `fastapi.Header`

### `router.py`
> Google OAuth login and callback routes.

- `async login_google(request)` `@router.get('/google')` (line 27)
  > Redirect user to Google OAuth consent screen.
- `async auth_google_callback(request)` `@router.get('/google/callback')` (line 34)
  > Handle Google OAuth callback, create or update user, issue JWT.
- `async me(user)` `@router.get('/me')` (line 72)
  > Return the authenticated user's profile.

  **Calls to other modules:**
  - `auth_google_callback` → `app.db.engine.AsyncSessionLocal`
  - `auth_google_callback` → `fastapi.responses.RedirectResponse`
  - `auth_google_callback` → `app.db.models.User`
  - `auth_google_callback` → `app.auth.dependencies.create_jwt`
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
  > Create all database tables from SQLAlchemy models.

### `models.py`
> SQLAlchemy ORM models for users, sessions, agent runs, and chat.

- **class `Base(DeclarativeBase)`** (line 13)
  > Base class for all ORM models.
- **class `User(Base)`** (line 23)
  > Stores user account data from OAuth providers.
- **class `Session(Base)`** (line 38)
  > Stores pipeline session state and data blobs.
- **class `SessionFile(Base)`** (line 93)
  > Stores per-file data for multi-file uploads.
- **class `AgentRun(Base)`** (line 106)
  > Stores agent loop run state and champion model.
- **class `AgentIteration(Base)`** (line 127)
  > Stores per-iteration results within an agent run.
- **class `ChatMessage(Base)`** (line 143)
  > Stores chat messages between user and agent.
- `utcnow()` (line 18)
  > Return the current UTC datetime.

  **Calls to other modules:**
  - `utcnow` → `datetime.datetime.now`

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

- **class `ColumnRole(str, Enum)`** (line 9)
  > Column semantic roles for mapping.
- **class `RiskTier(str, Enum)`** (line 22)
  > Churn risk classification tiers.
- **class `ColumnProfile(BaseModel)`** (line 31)
  > Profile statistics for a single column.
- **class `DataProfile(BaseModel)`** (line 40)
  > Profile statistics for an uploaded dataset.
- **class `UploadResponse(BaseModel)`** (line 48)
  > Response for single file upload.
- **class `FileProfile(BaseModel)`** (line 54)
  > Profile for a single file in a multi-file upload.
- **class `MultiUploadResponse(BaseModel)`** (line 60)
  > Response for multi-file upload.
- **class `ColumnMapping(BaseModel)`** (line 68)
  > Maps a column name to its detected role.
- **class `ColumnMappingResponse(BaseModel)`** (line 76)
  > Response containing column-to-role mappings.
- **class `ColumnMappingOverride(BaseModel)`** (line 81)
  > Request to override column mappings.
- **class `ColumnMappingFeedback(BaseModel)`** (line 86)
  > Request to re-map columns with user feedback.
- **class `JoinStep(BaseModel)`** (line 92)
  > Describes a single join operation between two files.
- **class `LLMJoinStrategy(BaseModel)`** (line 101)
  > LLM output for multi-file join strategy.
- **class `MCQOption(BaseModel)`** (line 109)
  > A single option in a multiple choice question.
- **class `MCQuestion(BaseModel)`** (line 115)
  > A multiple choice question for business context.
- **class `BusinessHypothesis(BaseModel)`** (line 123)
  > LLM-generated business type hypothesis.
- **class `HypothesisRequest(BaseModel)`** (line 130)
  > Request body for hypothesis generation.
- **class `HypothesisResponse(BaseModel)`** (line 135)
  > Response containing hypothesis and MCQ questions.
- **class `MCQAnswers(BaseModel)`** (line 143)
  > User answers to MCQ questions.
- **class `FeatureStat(BaseModel)`** (line 148)
  > Statistics for a single computed feature.
- **class `FeaturesResponse(BaseModel)`** (line 156)
  > Response containing computed features and statistics.
- **class `LabelsResponse(BaseModel)`** (line 166)
  > Response containing churn label statistics.
- **class `ConfusionMatrix(BaseModel)`** (line 177)
  > Confusion matrix counts.
- **class `FeatureImportance(BaseModel)`** (line 185)
  > Feature name with its importance score.
- **class `TrainResponse(BaseModel)`** (line 191)
  > Response containing training metrics and feature importance.
- **class `SamplePrediction(BaseModel)`** (line 201)
  > A single customer prediction with risk tier.
- **class `ResultsResponse(BaseModel)`** (line 209)
  > Response containing model results summary and predictions.
- **class `FeatureContribution(BaseModel)`** (line 219)
  > SHAP-based feature contribution for a prediction.
- **class `InferencePrediction(BaseModel)`** (line 225)
  > A single customer inference prediction with feature contributions.
- **class `InferenceResponse(BaseModel)`** (line 233)
  > Response containing inference predictions for all customers.
- **class `LLMColumnMappingItem(BaseModel)`** (line 244)
  > LLM output for a single column mapping.
- **class `LLMColumnMappingOutput(BaseModel)`** (line 251)
  > LLM output for column mapping.
- **class `LLMMCQOption(BaseModel)`** (line 256)
  > LLM output for a MCQ option.
- **class `LLMMCQ(BaseModel)`** (line 262)
  > LLM output for a MCQ question.
- **class `LLMHypothesisOutput(BaseModel)`** (line 270)
  > LLM output for business hypothesis generation.
- **class `LLMFeatureSelectionOutput(BaseModel)`** (line 278)
  > LLM output for tier 2 feature selection.
- **class `LLMResultsSummaryOutput(BaseModel)`** (line 284)
  > LLM output for results summary text.
- **class `DSLFeature(BaseModel)`** (line 291)
  > Definition of a DSL-based feature with operation and parameters.
  - `params(self)` `@property`
    > Parse params_json string into a dict.
- **class `LLMFeatureSuggestionOutput(BaseModel)`** (line 305)
  > LLM output for DSL feature suggestions.
- **class `LLMEvaluationOutput(BaseModel)`** (line 311)
  > LLM output for model evaluation with leakage detection.
- **class `LLMChatOutput(BaseModel)`** (line 322)
  > LLM output for chat message classification.
- **class `ModelResultSchema(BaseModel)`** (line 330)
  > Schema for serialized model results in API responses.
- **class `IterationResultSchema(BaseModel)`** (line 339)
  > Schema for a single agent iteration result.
- **class `AgentStatusResponse(BaseModel)`** (line 351)
  > Response for agent loop status.
- **class `SessionListItem(BaseModel)`** (line 363)
  > Schema for a session in the session list.
- **class `RenameRequest(BaseModel)`** (line 375)
  > Request body for renaming a session.
- **class `UserInfo(BaseModel)`** (line 380)
  > Schema for user profile information.

  **Calls to other modules:**
  - `DSLFeature.params` → `json.json.loads`

## `app/stages/`

### `s1_upload.py`
> Stage 1: CSV file upload, parsing, and profiling.

- `async handle_multi(files, description, user_id)` (line 20)
  > Parse and profile multiple uploaded CSV files.
- `async handle(file, user_id)` (line 78)
  > Parse and profile a single uploaded CSV file.
- `_build_profile(df)` (line 110)
  > Build a DataProfile from a DataFrame.
- `_infer_dtype(series)` (line 155)
  > Infer the semantic data type of a pandas Series.

  **Calls to other modules:**
  - `handle_multi` → `app.models.schemas.FileProfile`
  - `handle_multi` → `fastapi.HTTPException`
  - `handle_multi` → `app.models.schemas.MultiUploadResponse`
  - `handle_multi` → `io.io.BytesIO`
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

- `async handle(session_id, session)` (line 20)
  > Run LLM column mapping on the session profile.
- `handle_override(session_id, session, body)` (line 49)
  > Replace column mappings with user-provided overrides.
- `async handle_with_feedback(session_id, session, body)` (line 61)
  > Re-run LLM column mapping with user feedback.
- `_build_prompt(profile, file_description)` (line 109)
  > Build the LLM prompt for column role detection.
- `async join_files(session_id, session)` (line 154)
  > Join multiple uploaded files into a single DataFrame using LLM-determined strategy.

Returns a dict with 'dataframe', 'join_summary' keys.
If session has a single file or already has a dataframe, returns it directly.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.ColumnMapping`
  - `handle` → `app.models.schemas.ColumnMappingResponse`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.llm.client.generate_structured`
  - `handle` → `app.session_store.store.update`
  - `handle_override` → `app.models.schemas.ColumnMappingResponse`
  - `handle_override` → `app.session_store.store.update`
  - `handle_with_feedback` → `app.models.schemas.ColumnMapping`
  - `handle_with_feedback` → `app.models.schemas.ColumnMappingResponse`
  - `handle_with_feedback` → `fastapi.HTTPException`
  - `handle_with_feedback` → `app.llm.client.generate_structured`
  - `handle_with_feedback` → `app.session_store.store.update`
  - `join_files` → `fastapi.HTTPException`
  - `join_files` → `app.llm.client.generate_structured`
  - `join_files` → `pandas.pd.merge`
  - `join_files` → `app.session_store.store.update`

### `s3_hypothesis.py`
> Stage 3: Business hypothesis generation and MCQ question creation.

- `async handle(session_id, session, free_text)` (line 16)
  > Generate business hypothesis and MCQ questions using LLM.
- `_build_prompt(profile, column_mapping, free_text)` (line 56)
  > Build the LLM prompt for hypothesis and question generation.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.BusinessHypothesis`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.HypothesisResponse`
  - `handle` → `app.models.schemas.MCQOption`
  - `handle` → `app.models.schemas.MCQuestion`
  - `handle` → `app.llm.client.generate_structured`
  - `handle` → `app.llm.client.get_reasoning_model`
  - `handle` → `app.session_store.store.update`

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
  > Compute feature matrix from data using MCQ answers for configuration.
- `async _extract_user_features(free_text, col_map, existing_features)` (line 507)
  > Translate user free text into DSL feature definitions via LLM.
- `_build_col_map(column_mapping)` (line 554)
  > Map role -> column name from the column mapping.
- `_get_available_tier2(col_map)` (line 564)
  > Return Tier 2 feature names whose required columns exist.
- `compute_feature_matrix(df_obs, col_map, column_mapping, hypothesis, mcq_answers, excluded_features, dsl_features)` (line 573)
  > Compute features from observation window data.

Returns (feature_matrix, tier1_names, tier2_names, dsl_names).
This function is used by both the stage handler and the agent loop.
- `async compute_feature_matrix_async(df_obs, col_map, column_mapping, hypothesis, mcq_answers, excluded_features, dsl_features)` (line 658)
  > Async version of compute_feature_matrix. Used by agent loop.
- `async _select_tier2_features(available, column_mapping, hypothesis, mcq_answers)` (line 717)
  > Ask LLM to select which tier 2 features to compute.

  **Calls to other modules:**
  - `compute_recency` → `pandas.pd.to_datetime`
  - `compute_recency` → `pandas.pd.to_datetime(g[date_col]).max`
  - `_frequency_window` → `pandas.pd.Timedelta`
  - `_frequency_window` → `pandas.pd.to_datetime`
  - `compute_frequency_trend` → `pandas.pd.to_datetime`
  - `compute_monetary_trend` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_avg` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_avg` → `pandas.pd.to_datetime(g[date_col]).sort_values`
  - `compute_days_between_purchases_std` → `pandas.pd.to_datetime`
  - `compute_days_between_purchases_std` → `pandas.pd.to_datetime(g[date_col]).sort_values`
  - `compute_peak_vs_offpeak_ratio` → `pandas.pd.to_datetime`
  - `compute_order_size_trend` → `pandas.pd.to_datetime`
  - `compute_product_mix_change` → `pandas.pd.to_datetime`
  - `compute_weekend_vs_weekday` → `pandas.pd.to_datetime`
  - `compute_max_gap_between_purchases` → `pandas.pd.to_datetime`
  - `compute_max_gap_between_purchases` → `pandas.pd.to_datetime(g[date_col]).sort_values`
  - `compute_purchase_regularity_score` → `pandas.pd.to_datetime`
  - `compute_purchase_regularity_score` → `pandas.pd.to_datetime(g[date_col]).sort_values`
  - `handle` → `app.models.schemas.FeatureStat`
  - `handle` → `app.models.schemas.FeaturesResponse`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.stages.s5_labels._get_churn_window`
  - `handle` → `app.agent.feature_dsl.execute_dsl_features`
  - `handle` → `pandas.pd.DataFrame`
  - `handle` → `pandas.pd.Timedelta`
  - `handle` → `pandas.pd.to_datetime`
  - `handle` → `app.session_store.store.update`
  - `_extract_user_features` → `app.llm.client.generate_structured`
  - `compute_feature_matrix` → `asyncio.asyncio.get_running_loop`
  - `compute_feature_matrix` → `asyncio.asyncio.run`
  - `compute_feature_matrix` → `app.agent.feature_dsl.execute_dsl_features`
  - `compute_feature_matrix` → `pandas.pd.DataFrame`
  - `compute_feature_matrix_async` → `app.agent.feature_dsl.execute_dsl_features`
  - `compute_feature_matrix_async` → `pandas.pd.DataFrame`
  - `_select_tier2_features` → `app.llm.client.generate_structured`

### `s5_labels.py`
> Stage 5: Churn label assignment based on cutoff date.

- `handle(session_id, session)` (line 10)
  > Assign churn labels and return label statistics.
- `_assign_labels(df, col_map, cutoff_date)` (line 85)
  > Assign churn labels: 1 if no purchase after cutoff, 0 otherwise.
- `_get_churn_window(df, col_map, mcq_answers)` (line 105)
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
  - `_get_churn_window` → `pandas.pd.to_datetime(g[date_col]).sort_values`

### `s6_train.py`
> Stage 6: XGBoost model training with stratified split.

- `handle(session_id, session)` (line 25)
  > Train an XGBoost model and return metrics.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.ConfusionMatrix`
  - `handle` → `app.models.schemas.FeatureImportance`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.TrainResponse`
  - `handle` → `sklearn.metrics.confusion_matrix`
  - `handle` → `sklearn.metrics.f1_score`
  - `handle` → `sklearn.metrics.precision_score`
  - `handle` → `sklearn.metrics.recall_score`
  - `handle` → `sklearn.metrics.roc_auc_score`
  - `handle` → `app.session_store.store.update`
  - `handle` → `time.time.time`
  - `handle` → `sklearn.model_selection.train_test_split`
  - `handle` → `xgboost.xgb.XGBClassifier`

### `s7_results.py`
> Stage 7: Model results summary with LLM-generated text.

- `async handle(session_id, session)` (line 15)
  > Build results response with sample predictions and LLM summary.
- `_get_risk_tier(probability)` (line 60)
  > Map a churn probability to a risk tier.
- `async _generate_summary(metrics, feature_importance, business_type)` (line 69)
  > Generate a text summary of model results using LLM.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.FeatureImportance`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.ResultsResponse`
  - `handle` → `app.models.schemas.SamplePrediction`
  - `_generate_summary` → `app.llm.client.generate_structured`

### `s8_inference.py`
> Stage 8: Churn inference with SHAP-based feature contributions.

- `handle(session_id, session)` (line 18)
  > Run churn predictions on all customers with SHAP explanations.
- `handle_download(session_id, session)` (line 107)
  > Generate a CSV download buffer from stored predictions.
- `_get_risk_tier(probability)` (line 157)
  > Map a churn probability to a risk tier.

  **Calls to other modules:**
  - `handle` → `app.models.schemas.FeatureContribution`
  - `handle` → `fastapi.HTTPException`
  - `handle` → `app.models.schemas.InferencePrediction`
  - `handle` → `app.models.schemas.InferenceResponse`
  - `handle` → `numpy.np.abs`
  - `handle` → `numpy.np.argsort`
  - `handle` → `shap.shap.TreeExplainer`
  - `handle` → `app.session_store.store.update`
  - `handle_download` → `fastapi.HTTPException`
  - `handle_download` → `io.io.StringIO`
  - `handle_download` → `pandas.pd.DataFrame`
