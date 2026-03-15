# DotAI AutoModel - Churn Prediction ML Tool

## Objective
A Sales VP at a 10,000 Cr company uploads their transaction CSV. Within 5 minutes, the tool produces a list of at-risk customers with names, risk levels, and what changed in their behavior — verified against the VP's own history. The VP recognizes customers they lost, trusts the model, and hands the list to their field team that week.

The goal is not prediction accuracy. The goal is trust. The VP has been burned by data science projects that delivered PDFs with AUC scores. This tool delivers names they can check, reasons they can verify, and a file they can act on.

Every design decision serves this: verify first, then trust, then act.

## Target Users
- Sales VPs / distribution heads at Indian companies selling physical products through dealer/distributor networks
- 19 verticals: FMCG, dairy, paints, adhesives, cement, wires, tiles, steel, consumer durables, tyres, batteries, lubricants, auto OEM, auto aftermarket, pharma, agri, textiles, footwear, telecom
- 5 data types: transaction-only, transaction+service, transaction+loyalty, transaction+returns, transaction+field interaction
- Most companies overlap multiple data types (e.g., Pidilite = transaction + loyalty + field)

## Overview
Churn prediction system with an 8-stage ML pipeline, LLM-based evaluation, agent loop, WebSocket chat, and Google OAuth. Built with FastAPI (backend) and vanilla JS (frontend).

## Communication Style
- Do not use adjectives or adverbs in responses

---

## Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8000

# Test
pytest tests/ --ignore=tests/test_pipeline.py -q
```

- `pytest.ini` has `asyncio_mode = auto` for async test support
- `test_pipeline.py` requires a running server -- exclude it in unit test runs

---

## Render Deployment

### Web Service
| Setting | Value |
|---------|-------|
| Name | `churn-tool` |
| ID | `srv-d6hbkpvgi27c73fnkp30` |
| URL | https://churn-tool.onrender.com |
| Dashboard | https://dashboard.render.com/web/srv-d6hbkpvgi27c73fnkp30 |
| Runtime | Python, Starter plan, Oregon |
| Branch | `main` (auto-deploy on push) |
| Build | `pip install -r requirements.txt` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Database
| Setting | Value |
|---------|-------|
| Name | `churn-db` |
| ID | `dpg-d6hbkm3uibrs739sjf10-a` |
| Dashboard | https://dashboard.render.com/d/dpg-d6hbkm3uibrs739sjf10-a |
| Plan | Free (expires 2026-03-30) |
| DB Name | `churn_db_h4wr` |
| User | `churn_db_h4wr_user` |

### Render MCP Access
Use `mcp__render__*` tools with service ID `srv-d6hbkpvgi27c73fnkp30`.

---

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `JWT_SECRET` - JWT signing secret
- `GEMINI_API_KEY` - Google Gemini API key
- `GROQ_API_KEY` - Groq API key
- `GOOGLE_CHAT_WEBHOOK_URL` - Google Chat webhook for notifications
- `APP_BASE_URL` - Base URL of the app (e.g., https://churn-tool.onrender.com)

---

## Project Documentation (start here for context)

Read these auto-generated indexes to understand the codebase:

1. **[documentation/MASTER_INDEX.md](documentation/MASTER_INDEX.md)** — Project overview, backend/frontend structure, API contract (backend ↔ frontend mapping), config files
2. **[documentation/backend/INDEX.md](documentation/backend/INDEX.md)** — All Python files, functions with docstrings, cross-file call graph, API routes
3. **[documentation/frontend/INDEX.md](documentation/frontend/INDEX.md)** — All frontend files, JS functions, fetch calls, WebSocket connections

These indexes are regenerated on every file write/edit via a PostToolUse hook (`scripts/generate_docs.py`). When adding or modifying Python code, write a one-line docstring for each function and class — the index extracts these.

---

## Architecture

### 8-Stage ML Pipeline
1. Data upload
2. Schema detection
3. Feature engineering (DSL-based)
4. Data preprocessing
5. Target selection
6. Model training (multi-model)
7. LLM evaluation
8. Inference

### Components
- **Agent Loop** (`app/agent/`) - Orchestrates pipeline stages with LLM decisions
- **WebSocket Chat** (`app/chat/`) - Real-time communication during pipeline runs
- **Google OAuth** (`app/auth/`) - Authentication via Google SSO
- **Persistence** (`app/persistence.py`) - Session and pipeline state management
- **Notifications** (`app/notifications.py`) - Google Chat webhook alerts

### Code Notes
- Pydantic: Use `model_config = {"protected_namespaces": ()}` for fields like `model_results`
- pandas: `groupby().apply()` needs `include_groups=False` to avoid deprecation warnings
- Static files mounted at `/` in `app/main.py` (catch-all, must be last)
