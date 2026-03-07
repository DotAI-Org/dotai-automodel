# Database Schema

PostgreSQL database (`churn`). Tables created on startup via SQLAlchemy `metadata.create_all()`.

## Tables

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| name | VARCHAR(255) | |
| avatar_url | TEXT | |
| provider | VARCHAR(20) | default 'google' |
| provider_id | VARCHAR(255) | Google subject ID |
| created_at | TIMESTAMPTZ | default now |

### sessions

| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(12) | PK (hex ID) |
| user_id | UUID | FK -> users.id, NOT NULL |
| name | VARCHAR(255) | user-editable display name |
| filename | VARCHAR(255) | original CSV name |
| status | VARCHAR(20) | default 'upload' |
| stage | INTEGER | default 1 |
| created_at | TIMESTAMPTZ | default now |
| updated_at | TIMESTAMPTZ | default now, auto-updated |
| profile | JSONB | data profile from upload |
| file_description | TEXT | user description |
| column_mapping | JSONB | LLM column roles |
| hypothesis | JSONB | business hypothesis |
| free_text | TEXT | user domain knowledge |
| mcq_answers | JSONB | user MCQ answers |
| col_map | JSONB | role -> column name map |
| tier1_features | JSONB | |
| tier2_features | JSONB | |
| user_dsl_features | JSONB | |
| churn_window_days | INTEGER | |
| cutoff_date | VARCHAR(20) | |
| metrics | JSONB | {auc, f1, precision, recall} |
| confusion_matrix_data | JSONB | |
| feature_importance | JSONB | |
| training_time_seconds | FLOAT | |
| feature_names | JSONB | |
| dataframe_blob | BYTEA | compressed pickle of DataFrame |
| feature_matrix_blob | BYTEA | compressed pickle |
| labels_blob | BYTEA | compressed pickle |
| labeled_features_blob | BYTEA | compressed pickle |
| model_blob | BYTEA | compressed pickle of trained model |
| x_test_blob | BYTEA | compressed pickle |
| y_test_blob | BYTEA | compressed pickle |
| predictions_blob | BYTEA | compressed pickle |

**Indexes:** `idx_sessions_user_id` (user_id), `idx_sessions_updated_at` (updated_at)

### session_files

For multi-file uploads. Each file stored separately.

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| session_id | VARCHAR(12) | FK -> sessions.id, CASCADE |
| filename | VARCHAR(255) | |
| profile | JSONB | |
| dataframe_blob | BYTEA | compressed pickle |

### agent_runs

One row per agent execution.

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| session_id | VARCHAR(12) | FK -> sessions.id, CASCADE |
| status | VARCHAR(20) | default 'running' |
| iteration | INTEGER | default 0 |
| max_iterations | INTEGER | default 5 |
| excluded_features | JSONB | |
| dsl_features | JSONB | |
| success_criteria | JSONB | |
| champion | JSONB | champion model metadata |
| champion_model_blob | BYTEA | compressed pickle |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### agent_iterations

One row per iteration within an agent run.

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| agent_run_id | INTEGER | FK -> agent_runs.id, CASCADE |
| iteration | INTEGER | |
| features_used | JSONB | |
| features_removed | JSONB | |
| features_added | JSONB | |
| model_results | JSONB | |
| evaluation | JSONB | |

### chat_messages

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PK |
| session_id | VARCHAR(12) | FK -> sessions.id, CASCADE |
| role | VARCHAR(20) | 'user', 'system', 'progress' |
| content | TEXT | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | |

## Blob Serialization

Binary columns use `zlib.compress(pickle.dumps(obj, protocol=5))`. Deserialization: `pickle.loads(zlib.decompress(data))`.

See `app/persistence.py` for the mapping between in-memory dict keys and DB column names.

## Relationships

- User -> Sessions (1:N, cascade delete)
- Session -> SessionFiles (1:N, cascade delete)
- Session -> AgentRuns (1:N, cascade delete)
- Session -> ChatMessages (1:N, cascade delete)
- AgentRun -> AgentIterations (1:N, cascade delete)
