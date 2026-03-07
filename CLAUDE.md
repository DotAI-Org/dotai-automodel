# DotAI AutoModel - Churn Prediction ML Tool

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
