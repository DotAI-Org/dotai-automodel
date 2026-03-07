# Churn Tool — Context

## Starting the Application

### Prerequisites
- Python 3.11+ with virtual env at `churn-tool/venv/`
- `backend/.env.local` must exist with LLM keys (loaded automatically by `app/main.py`)

### Environment Variables (from `backend/.env.local`)
```
GROQ_API_KEY=<key>
GEMINI_API_KEY=<key>
LLM_PROVIDER=gemini   # "gemini" or "groq"
GEMINI_MODEL=<optional override>
```

The app loads `../../backend/.env.local` relative to `app/main.py` at startup.

### Start Server
```bash
cd churn-tool
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Frontend
Open `http://localhost:8000` in a browser. Static files are mounted at `/` (catch-all, last route).

### Run Tests
```bash
# Unit tests only
./venv/bin/pytest tests/unit/ -v

# All tests except pipeline (requires running server)
./venv/bin/pytest --ignore=tests/test_pipeline.py -v

# Specific test file
./venv/bin/pytest tests/unit/test_feature_dsl.py -v
```

`pytest.ini` has `asyncio_mode = auto` for async test support.

---

## Architecture

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.115.0, Uvicorn |
| ML | XGBoost 2.1.1, scikit-learn 1.5.1, SHAP 0.45.1 |
| Data | pandas 2.2.2, NumPy 1.26.4 |
| LLM | google-genai 1.5.0 (Gemini), Groq (llama-3.3-70b-versatile) |
| Frontend | Single HTML page, vanilla JS, WebSocket |

### Pipeline Flow
```
Upload CSV → Column Mapping → Hypothesis/MCQs → Agent Loop → Results → Inference
                                                    │
                                              ┌─────┴──────┐
                                              │ Iterations  │
                                              │ (max 5):    │
                                              │  Features   │
                                              │  Labels     │
                                              │  Train      │
                                              │  Evaluate   │
                                              │  Adjust     │
                                              └─────────────┘
```

Users can interact via WebSocket chat during the agent loop.

---

## File Structure

```
churn-tool/
├── app/
│   ├── main.py                  # FastAPI app, all routes, static mount
│   ├── session_store.py         # In-memory session store, 24h TTL
│   ├── agent/
│   │   ├── loop.py              # Agent loop orchestration (max 5 iterations)
│   │   ├── evaluator.py         # LLM leakage detection + quality checks
│   │   ├── model_trainer.py     # XGBoost + Random Forest training
│   │   ├── feature_dsl.py       # DSL interpreter (8 operations)
│   │   └── feature_engineer.py  # LLM feature suggestion via DSL
│   ├── chat/
│   │   ├── router.py            # WebSocket endpoint
│   │   └── handler.py           # Chat message classification + dispatch
│   ├── stages/
│   │   ├── s1_upload.py         # CSV upload + profiling
│   │   ├── s2_column_map.py     # Column role inference (LLM)
│   │   ├── s3_hypothesis.py     # Business hypothesis + MCQs (LLM)
│   │   ├── s4_features.py       # Tier 1 + Tier 2 feature computation
│   │   ├── s5_labels.py         # Churn label generation
│   │   ├── s6_train.py          # Model training (standalone)
│   │   ├── s7_results.py        # LLM result summary
│   │   └── s8_inference.py      # SHAP + per-customer predictions
│   ├── models/
│   │   └── schemas.py           # All Pydantic models
│   └── llm/
│       └── client.py            # Gemini/Groq abstraction with retry
├── static/
│   └── index.html               # Single-page chat UI
├── tests/
│   ├── unit/                    # 11 unit test files
│   ├── integration/             # 4 integration test files
│   ├── edge/                    # Edge case tests
│   ├── test_data/               # 4 CSV files for testing
│   ├── generators/              # Test data generators
│   ├── conftest.py              # Shared fixtures
│   └── test_pipeline.py         # Full pipeline test (needs server)
├── requirements.txt
├── pytest.ini
└── venv/                        # Virtual environment
```

---

## API Endpoints

### Stage Endpoints (sequential pipeline)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sessions` | Upload CSV, get session_id + data profile |
| POST | `/sessions/{id}/column-mapping` | Auto-map columns via LLM |
| PUT | `/sessions/{id}/column-mapping` | Manual column mapping override |
| POST | `/sessions/{id}/hypothesis` | Generate business hypothesis + MCQs |
| POST | `/sessions/{id}/features` | Compute Tier 1 + Tier 2 features |
| POST | `/sessions/{id}/labels` | Generate churn labels |
| POST | `/sessions/{id}/train` | Train model (standalone) |
| GET | `/sessions/{id}/results` | LLM summary of results |
| POST | `/sessions/{id}/inference` | SHAP + per-customer predictions |
| GET | `/sessions/{id}/inference/download` | Download predictions CSV |

### Agent Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sessions/{id}/agent/start` | Start agent loop (background) |
| GET | `/sessions/{id}/agent/status` | Get agent state |
| POST | `/sessions/{id}/agent/stop` | Interrupt agent loop |

### WebSocket
| Protocol | Endpoint | Purpose |
|----------|----------|---------|
| WS | `/sessions/{id}/chat` | Chat + progress streaming |

**WebSocket message types (server → client):**
- `agent_progress` — status updates during iterations
- `iteration_result` — model metrics per iteration
- `agent_response` — text responses to user chat
- `champion_selected` — final model selection

---

## Agent Loop Details

### State Tracking
```
AgentState:
  iteration: 0-5
  status: running | success | completed | failed | interrupted
  history: list[IterationResult]
  champion: ModelResult | None
  excluded_features: list[str]
  dsl_features: list[DSLFeature]
  success_criteria: {min_auc: 0.7, min_f1: 0.5, max_top_feature_importance: 0.80, min_features_above_5pct: 3}
  user_overrides: dict (from chat commands)
```

### Each Iteration
1. Compute features (Tier 1 + Tier 2 + DSL features, minus excluded)
2. Compute labels (churn window based on hypothesis)
3. Train XGBoost + Random Forest
4. Evaluate via LLM (leakage detection + quality check)
5. Record results
6. Check for user overrides from chat
7. If quality acceptable and no leakage → select champion, stop
8. Otherwise → remove suspect features, ask LLM for new DSL features, loop

### Models Trained Per Iteration
| Model | Config |
|-------|--------|
| XGBoost | n_estimators=100, max_depth=5, learning_rate=0.1, scale_pos_weight=auto |
| Random Forest | n_estimators=100, max_depth=8, class_weight=balanced |

### Feature DSL Operations
| Operation | Description |
|-----------|------------|
| aggregate | Per-customer aggregation (sum, mean, count, etc.) |
| aggregate_window | Aggregation within N-day window |
| ratio | Ratio of two aggregations |
| trend | First-half vs second-half comparison |
| conditional_count | Count rows matching a condition |
| nunique | Distinct values per customer |
| gap_stat | Statistics on inter-purchase gaps |

---

## LLM Client

Dual provider support in `app/llm/client.py`:
- **Gemini**: google-genai SDK, `gemini-2.0-flash`, response schema for structured output
- **Groq**: OpenAI-compatible API, `llama-3.3-70b-versatile`, JSON mode

Retry logic: 3 attempts with exponential backoff (15s, 30s, 45s). Rate limit detection included.

Provider auto-detected based on which API key is present. `LLM_PROVIDER` env var overrides.

---

## Known Issues / Notes
- `IterationResultSchema` needs `model_config = {"protected_namespaces": ()}` due to `model_results` field
- pandas `groupby().apply()` needs `include_groups=False` to avoid deprecation warnings
- `test_pipeline.py` requires a running server — exclude with `--ignore=tests/test_pipeline.py`
- Static files mounted at `/` in `app/main.py` (catch-all, must be last route)
- Session store is in-memory with 24h TTL — data lost on server restart

---

## Test Data
| File | Location |
|------|----------|
| transactions.csv | `static/transactions.csv` and `tests/test_data/transactions.csv` |
| improvedTransactions.csv | `tests/test_data/improvedTransactions.csv` |
| ecommerce_sample.csv | `tests/test_data/ecommerce_sample.csv` |
| maturity_churn.csv | `tests/test_data/maturity_churn.csv` |
