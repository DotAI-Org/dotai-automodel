# Project Index — DotAI AutoModel

<!-- HAND-WRITTEN START -->







## About
Churn prediction system with an 8-stage ML pipeline, LLM-based evaluation,
agent loop, WebSocket chat, and Google OAuth.

## How to Run
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## How to Test
```bash
pytest tests/ --ignore=tests/test_pipeline.py -q
```

## How to Deploy
Push to `main` branch. Render auto-deploys from `main`.
URL: https://churn-tool.onrender.com
<!-- HAND-WRITTEN END -->

---
*Everything below is auto-generated. Do not edit.*

## Project Structure

- **Backend** (`app/`): 27 Python files → [backend/INDEX.md](backend/INDEX.md)
- **Frontend** (`static/`): 4 files → [frontend/INDEX.md](frontend/INDEX.md)
- **Config/Other**: 32 files

### Backend Folders

- `app/` — `main.py`, `notifications.py`, `persistence.py`, `session_store.py`
- `app/agent/` — `evaluator.py`, `feature_dsl.py`, `feature_engineer.py`, `loop.py`, `model_trainer.py`, `scoring.py`
- `app/auth/` — `config.py`, `dependencies.py`, `router.py`
- `app/chat/` — `handler.py`, `router.py`
- `app/db/` — `engine.py`, `models.py`
- `app/llm/` — `client.py`
- `app/models/` — `schemas.py`
- `app/stages/` — `s1_upload.py`, `s2_column_map.py`, `s3_hypothesis.py`, `s4_features.py`, `s5_labels.py`, `s6_train.py`, `s7_results.py`, `s8_inference.py`

## API Contract (Backend ↔ Frontend)

| Backend Route | Handler | Frontend Call | Frontend File |
|---------------|---------|---------------|---------------|
| `DELETE /api/sessions/{session_id}` | `delete_session()` in `app/main.py` | `*/sessions/*` | `static/index-old.html:178` |
| `GET /auth/google` | `login_google()` in `app/auth/router.py` | *no frontend call found* | - |
| `GET /auth/google/callback` | `auth_google_callback()` in `app/auth/router.py` | *no frontend call found* | - |
| `GET /auth/me` | `me()` in `app/auth/router.py` | `*/auth/me` | `static/index-old.html:42` |
| `GET /auth/me` | `me()` in `app/auth/router.py` | `*/auth/me` | `static/index.html:80` |
| `GET /auth/me` | `me()` in `app/auth/router.py` | `*/auth/me` | `static/prototype-hope.html:77` |
| `GET /health` | `health()` in `app/main.py` | *no frontend call found* | - |
| `GET /api/sessions` | `list_sessions()` in `app/main.py` | `*/sessions` | `static/index-old.html:102` |
| `GET /api/sessions` | `list_sessions()` in `app/main.py` | `*/sessions` | `static/index.html:184` |
| `GET /api/sessions` | `list_sessions()` in `app/main.py` | `*/sessions` | `static/index.html:265` |
| `GET /api/sessions` | `list_sessions()` in `app/main.py` | `*/sessions` | `static/prototype-hope.html:181` |
| `GET /api/sessions` | `list_sessions()` in `app/main.py` | `*/sessions` | `static/prototype-hope.html:254` |
| `GET /api/sessions/{session_id}/agent/status` | `agent_status()` in `app/main.py` | `*/sessions/*/agent/status` | `static/index-old.html:208` |
| `GET /api/sessions/{session_id}/agent/status` | `agent_status()` in `app/main.py` | `*/sessions/*/agent/status` | `static/index.html:237` |
| `GET /api/sessions/{session_id}/agent/status` | `agent_status()` in `app/main.py` | `*/sessions/*/agent/status` | `static/index.html:271` |
| `GET /api/sessions/{session_id}/agent/status` | `agent_status()` in `app/main.py` | `*/sessions/*/agent/status` | `static/index.html:732` |
| `GET /api/sessions/{session_id}/agent/status` | `agent_status()` in `app/main.py` | `*/sessions/*/agent/status` | `static/prototype-hope.html:234` |
| `GET /api/sessions/{session_id}/inference/download` | `inference_download()` in `app/main.py` | `*/sessions/*/inference/download` | `static/index.html:1014` |
| `GET /api/sessions/{session_id}/inference/download` | `inference_download()` in `app/main.py` | `*/sessions/*/inference/download` | `static/prototype-hope.html:903` |
| `GET /api/sessions/{session_id}/results` | `results()` in `app/main.py` | *no frontend call found* | - |
| `POST /api/sessions` | `create_session()` in `app/main.py` | `*/sessions` | `static/index-old.html:348` |
| `POST /api/sessions` | `create_session()` in `app/main.py` | `*/sessions` | `static/index.html:333` |
| `POST /api/sessions` | `create_session()` in `app/main.py` | `*/sessions` | `static/prototype-hope.html:310` |
| `POST /api/sessions/{session_id}/agent/start` | `start_agent()` in `app/main.py` | `*/sessions/*/agent/start` | `static/index-old.html:566` |
| `POST /api/sessions/{session_id}/agent/start` | `start_agent()` in `app/main.py` | `*/sessions/*/agent/start` | `static/index.html:612` |
| `POST /api/sessions/{session_id}/agent/start` | `start_agent()` in `app/main.py` | `*/sessions/*/agent/start` | `static/prototype-hope.html:585` |
| `POST /api/sessions/{session_id}/agent/stop` | `stop_agent()` in `app/main.py` | *no frontend call found* | - |
| `POST /api/sessions/{session_id}/column-mapping` | `column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/index-old.html:393` |
| `POST /api/sessions/{session_id}/column-mapping` | `column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/index.html:345` |
| `POST /api/sessions/{session_id}/column-mapping` | `column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/prototype-hope.html:322` |
| `POST /api/sessions/{session_id}/column-mapping/feedback` | `column_mapping_feedback()` in `app/main.py` | `*/sessions/*/column-mapping/feedback` | `static/index-old.html:446` |
| `POST /api/sessions/{session_id}/column-mapping/feedback` | `column_mapping_feedback()` in `app/main.py` | `*/sessions/*/column-mapping/feedback` | `static/index.html:455` |
| `POST /api/sessions/{session_id}/column-mapping/feedback` | `column_mapping_feedback()` in `app/main.py` | `*/sessions/*/column-mapping/feedback` | `static/prototype-hope.html:432` |
| `POST /api/sessions/{session_id}/features` | `features()` in `app/main.py` | `*/sessions/*/features` | `static/index-old.html:541` |
| `POST /api/sessions/{session_id}/features` | `features()` in `app/main.py` | `*/sessions/*/features` | `static/index.html:580` |
| `POST /api/sessions/{session_id}/features` | `features()` in `app/main.py` | `*/sessions/*/features` | `static/prototype-hope.html:557` |
| `POST /api/sessions/{session_id}/hypothesis` | `hypothesis()` in `app/main.py` | `*/sessions/*/hypothesis` | `static/index-old.html:495` |
| `POST /api/sessions/{session_id}/hypothesis` | `hypothesis()` in `app/main.py` | `*/sessions/*/hypothesis` | `static/index.html:524` |
| `POST /api/sessions/{session_id}/hypothesis` | `hypothesis()` in `app/main.py` | `*/sessions/*/hypothesis` | `static/prototype-hope.html:501` |
| `POST /api/sessions/{session_id}/inference` | `inference()` in `app/main.py` | `*/sessions/*/inference` | `static/index.html:874` |
| `POST /api/sessions/{session_id}/inference` | `inference()` in `app/main.py` | `*/sessions/*/inference` | `static/prototype-hope.html:768` |
| `POST /api/sessions/{session_id}/labels` | `labels()` in `app/main.py` | *no frontend call found* | - |
| `POST /api/sessions/{session_id}/train` | `train()` in `app/main.py` | *no frontend call found* | - |
| `POST /api/sessions/multi` | `create_session_multi()` in `app/main.py` | `*/sessions/multi` | `static/index-old.html:367` |
| `PUT /api/sessions/{session_id}/column-mapping` | `override_column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/index-old.html:474` |
| `PUT /api/sessions/{session_id}/column-mapping` | `override_column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/index.html:483` |
| `PUT /api/sessions/{session_id}/column-mapping` | `override_column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/index.html:503` |
| `PUT /api/sessions/{session_id}/column-mapping` | `override_column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/prototype-hope.html:460` |
| `PUT /api/sessions/{session_id}/column-mapping` | `override_column_mapping()` in `app/main.py` | `*/sessions/*/column-mapping` | `static/prototype-hope.html:480` |
| `PUT /api/sessions/{session_id}/name` | `rename_session()` in `app/main.py` | `*/sessions/*/name` | `static/index-old.html:162` |
| `WEBSOCKET /sessions/{session_id}/chat` | `chat_websocket()` in `app/chat/router.py` | *no frontend call found* | - |

## Configuration & Other Files

### `.env`
Environment variables: `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `GOOGLE_CHAT_WEBHOOK_URL`, `APP_BASE_URL`

### `.env.example`
Environment variables: `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `GOOGLE_CHAT_WEBHOOK_URL`, `APP_BASE_URL`

### `.gitignore`
Patterns: 9 entries

### `CLAUDE.md`
- DotAI AutoModel - Churn Prediction ML Tool
  - Objective
  - Target Users
  - Overview
  - Communication Style

### `documentation/AUTODOC_PLAN.md`
- AutoDoc System — Build Plan
  - Objective
  - Architecture
    - Three Parsers
    - Output: Tiered Index Files

### `documentation/MASTER_INDEX.md`
- Project Index — DotAI AutoModel
  - About
  - How to Run
  - How to Test
  - How to Deploy

### `documentation/TargetMarket/CompanyList.md`
- Indian Companies Selling Physical Products — Revenue > 1,000 Cr
  - 1. FMCG / Packaged Goods
  - 2. Dairy
  - 3. Paints & Coatings
  - 4. Adhesives, Waterproofing & Construction Chemicals

### `documentation/TargetMarket/DataPoints.md`
- Data Points Available to Sales Heads — By Vertical
  - Data Type Framework
    - Type 1: Transaction-only
    - Type 2: Transaction + service records
    - Type 3: Transaction + loyalty/membership

### `documentation/TargetMarket/DataTypes.md`
- Data Types Available to a Sales Head
  - 1. Primary Sales (Factory/Depot to Dealer)
  - 2. Secondary Sales (Dealer to Retailer)
  - 3. Dealer/Customer Master
  - 4. Credit/Payment Aging

### `documentation/TargetMarket/HLD-LLD.md`
- HLD + LLD: Multi-Data-Type Pipeline with Exhaustive Field Analysis
  - High-Level Design
    - Current State
    - Target State
    - Architecture Changes

### `documentation/TargetMarket/Stage3-4-Bulletproofing.md`
- Bulletproofing Stage 3 and Stage 4 for Blind Entry
  - The Problem
  - Core Principle: Compute First, Hypothesize Second
  - The Exhaustive Field Analysis
    - Why Exhaustive

### `documentation/TargetMarket/UserTypeIdentification.md`
- User Type Identification and Multi-Data-Type Pipeline Changes
  - Problem
  - The 5 Data Types (recap)
  - Part 1: How We Identify the User Type
    - Step 1: File Upload — UI Affordance for Describing Files

### `documentation/automodel/STARTER.md`
- Churn Prediction Tool
  - Quick Start (Local)
- 1. Set env vars (or add to backend/.env.local — loaded automatically)
- 2. Create DB (if using jacpl-db-1 container)
- 3. Install dependencies

### `documentation/automodel/auth-flow.md`
- Auth Flow
  - Overview
  - Sequence
  - JWT Structure
  - Auth Middleware

### `documentation/automodel/backend-pipeline.md`
- AutoModel: Self-Service Churn Prediction Backend
  - Overview
  - Project Location
  - Tech Stack
  - Pipeline: 8 Stages

### `documentation/automodel/context.md`
- Churn Tool — Context
  - Starting the Application
    - Prerequisites
    - Environment Variables (from `backend/.env.local`)
    - Start Server

### `documentation/automodel/data-leakage-fix.md`
- Data Leakage in Churn Pipeline: Observation and Fix
  - Problem
    - How Leakage Occurs
    - Observed Symptoms
  - Fix: Observation/Prediction Time Split

### `documentation/automodel/database-schema.md`
- Database Schema
  - Tables
    - users
    - sessions
    - session_files

### `documentation/automodel/googletesting/test_plan_maturity_churn.md`
- Test Plan: Maturity-Based Churn Prediction
  - Objective
  - Simulation Strategy
  - Pipeline Verification Steps
  - Success Criteria

### `documentation/automodel/groqgeminifailuredocument.md`
- LLM Integration Test Failure Report
  - Test Executed
  - Result
  - Root Cause
    - What happened step by step

### `documentation/automodel/interaction-design-hope.md`
- Interaction Design (Hope Variant) — Churn Intervention Platform
  - The Person Using This
  - What This Tool Does
  - Design Principles
  - The Emotional Arc

### `documentation/automodel/interaction-design.md`
- Interaction Design — Churn Intervention Platform
  - The Person Using This
  - What This Tool Does
  - Design Principles
  - Screens

### `documentation/automodel/model-comparison.md`
- Model Comparison: XGBoost vs Random Forest, With and Without Recency
  - Dataset
  - Performance Summary
  - Feature Importance
  - Observations

### `documentation/automodel/pipeline-flow.md`
- Churn Prediction Pipeline — How It Works
  - Overview
  - Persistence
  - Stage 1: Upload
  - Stage 2: Column Mapping

### `documentation/automodel/sales-user-journey.md`
- Sales User Journey — Churn Prediction Tool
  - Who is this for
  - What the user cares about
  - Journey Overview
  - Screen 1: Login

### `documentation/automodel/test-results.md`
- Churn-Tool Test Suite: Implementation Report
  - Overview
  - Test Run Results
  - Files Created
    - Foundation

### `documentation/backend/INDEX.md`
- Backend Index
  - API Routes
  - `app/`
    - `main.py`
    - `notifications.py`

### `documentation/frontend/INDEX.md`
- Frontend Index
  - API Calls
  - WebSocket Connections
  - `static/index-old.html`
    - Functions

### `pytest.ini`
Sections: `pytest`

### `render.yaml`
Top-level keys: `services`, `databases`

### `requirements.txt`
Packages: `fastapi`, `uvicorn`, `websockets`, `python-multipart`, `pandas`, `numpy`, `xgboost`, `scikit-learn`, `shap`, `google-genai`, `pydantic`, `sqlalchemy`, `asyncpg`, `alembic`, `python-jose`, `authlib`, `httpx`, `groq`, `python-dotenv`, `itsdangerous`

### Other Symbols (via ctags)

**`pytest.ini`**: `asyncio_mode` (key), `markers` (key), `testpaths` (key)
