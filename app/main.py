import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.session_store import store
from app.auth.config import JWT_SECRET
from app.auth.dependencies import get_current_user
from app.models.schemas import (
    UploadResponse,
    MultiUploadResponse,
    ColumnMappingResponse,
    ColumnMappingOverride,
    ColumnMappingFeedback,
    HypothesisRequest,
    HypothesisResponse,
    MCQAnswers,
    FeaturesResponse,
    LabelsResponse,
    TrainResponse,
    ResultsResponse,
    InferenceResponse,
    AgentStatusResponse,
    SessionListItem,
    RenameRequest,
)
from app.stages import (
    s1_upload,
    s2_column_map,
    s3_hypothesis,
    s4_features,
    s5_labels,
    s6_train,
    s7_results,
    s8_inference,
)
from app.agent.loop import (
    run_agent,
    get_agent_state,
    set_agent_state,
    AgentState,
)
from app.chat.router import router as chat_router
from app.auth.router import router as auth_router
from app.notifications import notify_gchat

app = FastAPI(title="Churn Prediction Tool", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware required by authlib for OAuth state
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)

# Health check (before api_router so it's at /health)
@app.get("/health")
async def health():
    return {"status": "ok"}

# API router — all backend routes under /api
api_router = APIRouter(prefix="/api")

# Auth routes
api_router.include_router(auth_router)

# Chat WebSocket
api_router.include_router(chat_router)


# --- Helpers ---

async def get_session_with_auth(session_id: str, user: dict):
    """Load session, verify ownership."""
    session = store.get(session_id)
    if session is None:
        session = await store.get_or_load(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    owner = session.get("user_id") or await store.get_owner(session_id)
    if owner and str(owner) != str(user["id"]):
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# --- Session List / Rename / Delete ---

@api_router.get("/sessions", response_model=list[SessionListItem])
async def list_sessions(user: dict = Depends(get_current_user)):
    return await store.list_sessions(user["id"])


@api_router.put("/sessions/{session_id}/name")
async def rename_session(session_id: str, body: RenameRequest, user: dict = Depends(get_current_user)):
    await get_session_with_auth(session_id, user)
    await store.rename(session_id, body.name)
    return {"status": "ok"}


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    await get_session_with_auth(session_id, user)
    await store.delete(session_id)
    return {"status": "ok"}


# --- Stage 1: Upload ---

@api_router.post("/sessions", response_model=UploadResponse)
async def create_session(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    return await s1_upload.handle(file, user_id=user["id"])


@api_router.post("/sessions/multi", response_model=MultiUploadResponse)
async def create_session_multi(
    files: list[UploadFile] = File(...),
    description: str = Form(...),
    user: dict = Depends(get_current_user),
):
    return await s1_upload.handle_multi(files, description, user_id=user["id"])


# --- Stage 2: Column Mapping ---

@api_router.post("/sessions/{session_id}/column-mapping", response_model=ColumnMappingResponse)
async def column_mapping(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return await s2_column_map.handle(session_id, session)


@api_router.put("/sessions/{session_id}/column-mapping", response_model=ColumnMappingResponse)
async def override_column_mapping(session_id: str, body: ColumnMappingOverride, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return s2_column_map.handle_override(session_id, session, body)


@api_router.post("/sessions/{session_id}/column-mapping/feedback", response_model=ColumnMappingResponse)
async def column_mapping_feedback(session_id: str, body: ColumnMappingFeedback, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return await s2_column_map.handle_with_feedback(session_id, session, body)


# --- Stage 3: Hypothesis ---

@api_router.post("/sessions/{session_id}/hypothesis", response_model=HypothesisResponse)
async def hypothesis(session_id: str, body: HypothesisRequest = None, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    free_text = body.free_text if body else None
    return await s3_hypothesis.handle(session_id, session, free_text=free_text)


# --- Stage 4: Features ---

@api_router.post("/sessions/{session_id}/features", response_model=FeaturesResponse)
async def features(session_id: str, body: MCQAnswers, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return await s4_features.handle(session_id, session, body)


# --- Stage 5: Labels ---

@api_router.post("/sessions/{session_id}/labels", response_model=LabelsResponse)
async def labels(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return s5_labels.handle(session_id, session)


# --- Stage 6: Train ---

@api_router.post("/sessions/{session_id}/train", response_model=TrainResponse)
async def train(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return s6_train.handle(session_id, session)


# --- Stage 7: Results ---

@api_router.get("/sessions/{session_id}/results", response_model=ResultsResponse)
async def results(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return await s7_results.handle(session_id, session)


# --- Stage 8: Inference ---

@api_router.post("/sessions/{session_id}/inference", response_model=InferenceResponse)
async def inference(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    return s8_inference.handle(session_id, session)


@api_router.get("/sessions/{session_id}/inference/download")
async def inference_download(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)
    csv_buffer = s8_inference.handle_download(session_id, session)
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=churn_predictions.csv"},
    )


# --- Agent Endpoints ---

@api_router.post("/sessions/{session_id}/agent/start")
async def start_agent(session_id: str, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)

    existing = get_agent_state(session_id)
    if existing and existing.status == "running":
        raise HTTPException(status_code=409, detail="Agent already running")

    state = AgentState(session_id=session_id)
    set_agent_state(session_id, state)

    async def _run():
        s = store.get(session_id)
        if s:
            try:
                await run_agent(session_id, s)
            except Exception as e:
                logging.getLogger(__name__).error(f"Agent crashed: {e}")
                agent_st = get_agent_state(session_id)
                if agent_st:
                    agent_st.status = "failed"
                await notify_gchat("Agent crashed", f"session {session_id}, error={e}")

    background_tasks.add_task(_run)

    return {"status": "started", "session_id": session_id}


@api_router.get("/sessions/{session_id}/agent/status")
async def agent_status(session_id: str, user: dict = Depends(get_current_user)):
    session = await get_session_with_auth(session_id, user)

    # 1. Try in-memory
    state = get_agent_state(session_id)
    if state is not None:
        return state.to_dict()

    # 2. Try AgentRun table
    from app.db.engine import AsyncSessionLocal
    from app.persistence import load_agent_state
    async with AsyncSessionLocal() as db:
        db_state = await load_agent_state(db, session_id)
    if db_state is not None:
        return db_state

    # 3. Reconstruct minimal state from Session row (for sessions before this fix)
    if session.get("stage", 0) >= 6:
        metrics = session.get("metrics") or {}
        return {
            "session_id": session_id,
            "iteration": 0,
            "max_iterations": 5,
            "status": "success",
            "history": [],
            "champion": {
                "name": metrics.get("champion_name", ""),
                "metrics": metrics,
                "feature_importance": session.get("feature_importance", []),
                "confusion_matrix": session.get("confusion_matrix_data"),
                "training_time": session.get("training_time_seconds"),
            },
        }

    raise HTTPException(status_code=404, detail="Agent not started")


@api_router.post("/sessions/{session_id}/agent/stop")
async def stop_agent(session_id: str, user: dict = Depends(get_current_user)):
    await get_session_with_auth(session_id, user)
    state = get_agent_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Agent not started")

    state.user_overrides["stop"] = True
    return {"status": "stopping", "session_id": session_id}


# Include API router
app.include_router(api_router)


# Startup
@app.on_event("startup")
async def startup():
    from app.db.engine import init_db, engine
    await init_db()
    store.set_engine(engine)


# Mount static files last (catch-all)
_static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
