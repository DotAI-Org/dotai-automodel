# Churn Prediction Tool

A web app that takes customer transaction CSVs and produces a call list of at-risk customers. Users upload data, the system maps columns via LLM, generates hypotheses, and runs an agent loop that trains and evaluates models across iterations. The output is a ranked list of customers sorted by churn risk, with reasons for each.

## Quick Start (Local)

```bash
# 1. Set env vars (or add to backend/.env.local — loaded automatically)
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/churn"
export JWT_SECRET="dev-secret-change-in-prod"
export GOOGLE_CLIENT_ID="<from Google Cloud Console>"
export GOOGLE_CLIENT_SECRET="<from Google Cloud Console>"
export GROQ_API_KEY="<from Groq dashboard>"

# 2. Create DB (if using jacpl-db-1 container)
docker exec jacpl-db-1 psql -U user -d mydatabase -c "CREATE DATABASE churn;"

# 3. Install dependencies
cd churn-tool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run
uvicorn app.main:app --reload --port 8001
```

Tables are created on startup via `init_db()`. No migrations needed.

The app reads env vars from `backend/.env.local` if the file exists (see `app/main.py` lines 7-9).

---

## Deployment (Render)

### Service Configuration

| Setting | Value |
|---------|-------|
| Service name | `churn-tool` |
| Type | Web Service |
| Runtime | Python |
| Branch | `dev` |
| Root directory | `churn-tool/` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Starter |
| Region | Oregon |
| Auto-deploy | Yes (push to `dev` triggers deploy) |

### Deploy Process

1. Push to the `dev` branch on GitHub (`git push origin dev`)
2. Render detects the commit and starts a build
3. Build installs Python dependencies from `requirements.txt`
4. On success, Render starts the uvicorn process
5. The app connects to the Render-hosted PostgreSQL database
6. `init_db()` runs on startup and creates any missing tables

### Render Environment Variables

Set these in the Render dashboard under the churn-tool service:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Internal connection string from Render Postgres |
| `JWT_SECRET` | Secret string for signing JWTs |
| `GOOGLE_CLIENT_ID` | OAuth client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `APP_BASE_URL` | `https://churn-tool.onrender.com` |
| `GROQ_API_KEY` | API key for Groq LLM calls |

### Database

Render Postgres instance. The `DATABASE_URL` from Render starts with `postgres://`. The engine module (`app/db/engine.py`) converts this to `postgresql+asyncpg://` for SQLAlchemy async compatibility.

### URLs

| Resource | URL |
|----------|-----|
| Frontend + Backend | https://churn-tool.onrender.com |
| Health check | https://churn-tool.onrender.com/health |
| API base | https://churn-tool.onrender.com/api |

There is no separate frontend deployment. The FastAPI app serves `static/index.html` at `/` via a catch-all StaticFiles mount.

---

## Architecture

```
Browser (static/index.html)
   |
   |  HTTP REST + WebSocket
   v
FastAPI (app/main.py)
   |
   +-- /api/auth/*        Google OAuth + JWT
   +-- /api/sessions/*    Session CRUD + pipeline stages
   +-- /api/sessions/{id}/agent/*   Agent loop control
   +-- /api/sessions/{id}/chat      WebSocket (chat + progress broadcasts)
   |
   +-- PostgreSQL          sessions, users, agent_runs, agent_iterations, chat_messages
   +-- LLM (Groq)          column mapping, hypothesis, evaluation, feature suggestions
   +-- ML (scikit-learn, XGBoost, SHAP)   model training + inference
```

### File Structure

```
churn-tool/
├── app/
│   ├── main.py              FastAPI app, routes, middleware, static mount
│   ├── session_store.py     In-memory session store with DB persistence
│   ├── persistence.py       DB save/load helpers for sessions and chat
│   ├── auth/
│   │   ├── config.py        JWT_SECRET, Google client config
│   │   ├── dependencies.py  get_current_user, create_jwt, get_ws_user
│   │   └── router.py        /auth/google, /auth/google/callback, /auth/me
│   ├── chat/
│   │   ├── handler.py       LLM-powered chat message handler
│   │   └── router.py        WebSocket endpoint for chat + broadcast
│   ├── db/
│   │   ├── engine.py        SQLAlchemy async engine, init_db()
│   │   └── models.py        User, Session, SessionFile, AgentRun, AgentIteration, ChatMessage
│   ├── models/
│   │   └── schemas.py       Pydantic request/response models
│   ├── stages/
│   │   ├── s1_upload.py     CSV upload, profiling
│   │   ├── s2_column_map.py LLM column role assignment
│   │   ├── s3_hypothesis.py LLM hypothesis + MCQ generation
│   │   ├── s4_features.py   Feature computation (tier1, tier2, DSL)
│   │   ├── s5_labels.py     Churn label assignment
│   │   ├── s6_train.py      Model training
│   │   ├── s7_results.py    Results summary
│   │   └── s8_inference.py  SHAP-based inference + CSV download
│   └── agent/
│       ├── loop.py          Agent loop: iterate features → train → evaluate → adjust
│       ├── evaluator.py     LLM evaluation of model results (leakage, quality)
│       ├── feature_dsl.py   Execute DSL feature definitions
│       ├── feature_engineer.py  LLM-suggested features
│       ├── model_trainer.py XGBoost + Random Forest training
│       └── scoring.py       Composite score for model comparison
├── static/
│   ├── index.html           Frontend (integrated with backend APIs)
│   ├── index-old.html       Previous ML-focused frontend (preserved)
│   └── prototype-hope.html  Same as index.html (reference copy)
└── requirements.txt
```

### Single-File Frontend

The frontend is a single HTML file (`static/index.html`) with embedded CSS and JavaScript. No build step. No framework. FastAPI serves it via:

```python
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

This mount is registered last in `main.py` so all `/api` routes take priority. Any path not matching an API route falls through to the static file server, which serves `index.html` for `/`.

---

## Backend: How It Works

### Auth Flow

1. User clicks "Sign in with Google" → browser navigates to `/api/auth/google`
2. FastAPI redirects to Google OAuth consent screen
3. User authenticates with Google → Google redirects to `/api/auth/google/callback`
4. Callback exchanges the code for user info (email, name, avatar)
5. User is created or updated in the `users` table
6. A JWT is created (7-day expiry) containing `{id, email, name}`
7. Browser is redirected to `/?token=<JWT>`
8. Frontend JavaScript captures the `token` URL parameter, stores it in `localStorage`
9. All subsequent API calls include `Authorization: Bearer <JWT>` header
10. WebSocket auth uses `?token=<JWT>` query parameter

### Session Store

Sessions live in two places:

- **In-memory** (`app/session_store.py`): holds the working data (DataFrames, models, feature matrices) for active sessions. This is lost on server restart.
- **PostgreSQL** (`app/persistence.py`): persists session metadata, stage data (profile, column mapping, hypothesis, MCQ answers), and binary blobs (DataFrames, models stored as compressed pickle).

When a session is requested that is not in memory, the store loads it from the database (`get_or_load`).

### Pipeline Stages

Each stage is a module in `app/stages/`. The frontend calls them sequentially via REST APIs.

| Stage | Module | API | What It Does |
|-------|--------|-----|--------------|
| 1 | `s1_upload` | `POST /api/sessions` | Accepts CSV, profiles it (row count, column types, date range, sample rows). Returns `session_id` and `profile`. |
| 2 | `s2_column_map` | `POST /api/sessions/{id}/column-mapping` | Sends column names + sample data to Groq LLM. LLM assigns roles: `customer_id`, `transaction_date`, `amount`, `product`, `quantity`, `category`, `channel`, `region`, `other`. Returns mapping with confidence scores. User can override via PUT or re-run with feedback. |
| 3 | `s3_hypothesis` | `POST /api/sessions/{id}/hypothesis` | Takes optional free-text context. LLM generates a churn hypothesis and 3-5 MCQ questions about the business. |
| 4 | `s4_features` | `POST /api/sessions/{id}/features` | Takes MCQ answers. Computes a feature matrix: tier-1 features (RFM-based), tier-2 features (trend, behavioral), and DSL features (LLM-suggested). |
| 5 | `s5_labels` | (called by agent) | Assigns churn labels based on a time split. Uses the MCQ answers to determine the churn window (default 90 days). |
| 6 | `s6_train` | (called by agent) | Trains XGBoost and Random Forest on the feature matrix + labels. |
| 7 | `s7_results` | `GET /api/sessions/{id}/results` | Returns champion model metrics, feature importance, confusion matrix. |
| 8 | `s8_inference` | `POST /api/sessions/{id}/inference` | Runs the champion model on all customers. Uses SHAP to compute per-customer feature contributions. Returns `{total_users, high_risk_count, medium_risk_count, low_risk_count, predictions[]}`. |

### Agent Loop

The agent (`app/agent/loop.py`) automates stages 4-6 in a loop:

```
Start → Compute Features → Train Models → LLM Evaluate → Decision
                                                            |
                                              ┌─────────────┴─────────────┐
                                              │                           │
                                      Quality acceptable?          Leakage detected?
                                      No leakage?                  Quality not met?
                                              │                           │
                                        Select champion           Remove suspect features
                                        → Done                   Ask LLM for new features
                                                                  → Next iteration
```

Each iteration:
1. **Compute features** — tier-1 + tier-2 + DSL features, excluding any features flagged in prior iterations
2. **Train models** — XGBoost and Random Forest with train/test split
3. **LLM Evaluate** — Groq LLM checks for data leakage (features that trivially predict the label), checks model quality against criteria
4. **Decision**:
   - If quality is acceptable and no leakage → select champion, stop
   - If leakage detected → remove suspect features, ask LLM to suggest new features, iterate
   - If max iterations (5) reached → pick the model with the highest composite score across all iterations

The agent runs as a FastAPI `BackgroundTask`. Progress is broadcast to connected WebSocket clients.

### WebSocket Messages

The WebSocket at `/api/sessions/{id}/chat?token=JWT` serves two purposes:

1. **Agent progress broadcasts** — the agent loop pushes messages as it works
2. **User chat** — user can send questions, LLM responds with context about the session

Message types from server:

| Type | When | Key Fields |
|------|------|------------|
| `chat_history` | On WebSocket connect | `role`, `text` |
| `agent_progress` | During each agent step | `iteration`, `status`, `detail` |
| `iteration_result` | After each training round | `iteration`, `models[]`, `evaluation` |
| `agent_response` | Agent or chat message | `text` |
| `champion_selected` | Agent found a winner | `champion{name, metrics, feature_importance}` |

Message from client: `{"text": "user question"}` → server responds with `agent_response`.

---

## Frontend-Backend Integration

### Page States

The frontend has 5 screens, each mapped to backend state:

| Screen | Shown When | Backend Data Source |
|--------|-----------|---------------------|
| Landing | No JWT in localStorage | None |
| Upload | New session or stage < 3 | `POST /api/sessions` → profile, `POST .../column-mapping` → mappings |
| Business | Stage 3-4 | `POST .../hypothesis` → questions, `POST .../features` → submit answers |
| Building | Agent running | `POST .../agent/start`, WebSocket for progress |
| Results | Agent completed with champion | `POST .../inference` → predictions, `GET .../inference/download` → CSV |

### Session Restore

When a user clicks a session in the sidebar:

1. Frontend calls `GET /api/sessions/{id}/agent/status`
2. If agent completed with champion → show results screen, call inference
3. If agent running → show building screen, connect WebSocket
4. If no agent state → check session stage from the session list, show upload or business screen

### Auth in Frontend

```javascript
// Store
localStorage.getItem('churn_jwt')

// All API calls
function authFetch(url, opts = {}) {
  opts.headers = { Authorization: 'Bearer ' + getJwt(), ...(opts.headers || {}) };
  return fetch(url, opts);
}

// WebSocket
new WebSocket(`wss://host/api/sessions/${id}/chat?token=${jwt}`);
```

### Data Flow: Upload → Results

```
1. User drops CSV
   → POST /api/sessions (FormData with file)
   ← {session_id, profile: {columns, row_count, date_range}}

2. Auto column mapping
   → POST /api/sessions/{id}/column-mapping
   ← {columns: [{name, dtype, llm_role, confidence}]}

3. User approves mappings
   → PUT /api/sessions/{id}/column-mapping (with overrides)
   → Navigate to business screen

4. LLM generates questions
   → POST /api/sessions/{id}/hypothesis {free_text}
   ← {hypothesis, questions: [{id, question, options[]}]}

5. User answers MCQ
   → POST /api/sessions/{id}/features {answers: {q_id: value}}
   ← {feature_count, user_count}

6. Agent starts
   → POST /api/sessions/{id}/agent/start
   → Connect WebSocket
   ← Progress messages via WebSocket

7. Agent completes
   ← champion_selected via WebSocket
   → POST /api/sessions/{id}/inference
   ← {total_users, high_risk_count, medium_risk_count, low_risk_count, predictions[]}

8. Download
   → GET /api/sessions/{id}/inference/download
   ← CSV file stream
```

### Feature Name Translation

The frontend maps raw feature names to readable labels:

| Raw Feature | Display Label |
|-------------|---------------|
| `recency` | No recent purchases |
| `frequency_30d` | Purchase frequency (30 days) |
| `frequency_trend` | Purchase frequency declining |
| `monetary_avg` | Average order value |
| `monetary_trend` | Spending less over time |
| `days_between_purchases_avg` | Longer gaps between orders |
| `basket_diversity` | Fewer products per order |
| `category_concentration` | Stopped buying top category |
| `weekend_vs_weekday` | Shifted to weekend orders |

---

## Database Schema

6 tables, all created by SQLAlchemy on startup.

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique |
| name | VARCHAR(255) | |
| avatar_url | TEXT | Google profile picture |
| provider | VARCHAR(20) | "google" |
| provider_id | VARCHAR(255) | Google sub ID |
| created_at | TIMESTAMPTZ | |

### sessions
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(12) | Primary key (nanoid) |
| user_id | UUID | FK → users |
| name | VARCHAR(255) | User-given name |
| filename | VARCHAR(255) | Original CSV filename |
| status | VARCHAR(20) | upload/mapping/hypothesis/features/agent/results |
| stage | INTEGER | 1-6 |
| profile | JSONB | Upload profile (columns, row_count, date_range) |
| column_mapping | JSONB | LLM-assigned column roles |
| hypothesis | JSONB | LLM hypothesis output |
| mcq_answers | JSONB | User MCQ answers |
| col_map | JSONB | Resolved column name mapping |
| metrics | JSONB | Champion model metrics |
| feature_importance | JSONB | Champion feature importance |
| dataframe_blob | BYTEA | Compressed pickle of uploaded DataFrame |
| model_blob | BYTEA | Compressed pickle of trained model |
| feature_matrix_blob | BYTEA | Compressed pickle of feature matrix |
| ... | BYTEA | Other binary blobs (labels, predictions, test data) |

### session_files
Multi-file upload support. Each file gets its own profile and DataFrame blob.

### agent_runs
Tracks each agent execution: status, iteration count, champion info, excluded features.

### agent_iterations
One row per iteration: features used, features removed/added, model results (JSONB), evaluation (JSONB).

### chat_messages
| Column | Type |
|--------|------|
| session_id | VARCHAR(12) |
| role | VARCHAR(20) — "user" or "system" |
| content | TEXT |
| created_at | TIMESTAMPTZ |

---

## API Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/auth/google` | No | Redirect to Google OAuth |
| GET | `/api/auth/google/callback` | No | OAuth callback, issues JWT |
| GET | `/api/auth/me` | Yes | Current user info |
| GET | `/api/sessions` | Yes | List user sessions |
| POST | `/api/sessions` | Yes | Upload single CSV |
| POST | `/api/sessions/multi` | Yes | Upload multiple CSVs |
| PUT | `/api/sessions/{id}/name` | Yes | Rename session |
| DELETE | `/api/sessions/{id}` | Yes | Delete session |
| POST | `/api/sessions/{id}/column-mapping` | Yes | Run LLM column mapping |
| PUT | `/api/sessions/{id}/column-mapping` | Yes | Override column mapping |
| POST | `/api/sessions/{id}/column-mapping/feedback` | Yes | Re-run mapping with feedback |
| POST | `/api/sessions/{id}/hypothesis` | Yes | Generate hypothesis + MCQ |
| POST | `/api/sessions/{id}/features` | Yes | Submit MCQ, compute features |
| POST | `/api/sessions/{id}/labels` | Yes | Compute churn labels |
| POST | `/api/sessions/{id}/train` | Yes | Train models |
| GET | `/api/sessions/{id}/results` | Yes | Get results summary |
| POST | `/api/sessions/{id}/inference` | Yes | Run inference (SHAP) |
| GET | `/api/sessions/{id}/inference/download` | Yes | Download predictions CSV |
| POST | `/api/sessions/{id}/agent/start` | Yes | Start agent loop |
| GET | `/api/sessions/{id}/agent/status` | Yes | Agent status + history |
| POST | `/api/sessions/{id}/agent/stop` | Yes | Stop agent |
| WS | `/api/sessions/{id}/chat?token=` | Yes | Chat + progress WebSocket |

---

## Environment Variables

| Key | Required | Description |
|-----|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string (asyncpg format or Render postgres:// format) |
| `JWT_SECRET` | Yes | Secret for signing JWTs |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `APP_BASE_URL` | No | Base URL for OAuth redirect (defaults to request origin) |
| `GROQ_API_KEY` | Yes | Groq API key for LLM calls |

---

## Detailed Docs

- [Pipeline Flow](pipeline-flow.md) — stage-by-stage detail, feature DSL, agent loop
- [Database Schema](database-schema.md) — all tables, columns, indexes
- [Auth Flow](auth-flow.md) — OAuth sequence, JWT structure
- [Interaction Design](interaction-design.md) — frontend screen-by-screen specification
