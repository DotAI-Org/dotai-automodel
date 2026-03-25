"""FastAPI application entry point and route definitions."""
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
    FindingsConfirmRequest,
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
    """Return health check status."""
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
    """Return all sessions for the authenticated user."""
    return await store.list_sessions(user["id"])


@api_router.put("/sessions/{session_id}/name")
async def rename_session(session_id: str, body: RenameRequest, user: dict = Depends(get_current_user)):
    """Rename a session by ID."""
    await get_session_with_auth(session_id, user)
    await store.rename(session_id, body.name)
    return {"status": "ok"}


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    """Delete a session by ID."""
    await get_session_with_auth(session_id, user)
    await store.delete(session_id)
    return {"status": "ok"}


# --- Stage 1: Upload ---

@api_router.post("/sessions", response_model=UploadResponse)
async def create_session(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Upload a CSV file and create a new session."""
    try:
        return await s1_upload.handle(file, user_id=user["id"])
    except HTTPException:
        await notify_gchat(
            "Upload failed",
            f"user={user.get('email', 'unknown')}, file={file.filename}",
        )
        raise
    except Exception as e:
        await notify_gchat(
            "Upload failed",
            f"user={user.get('email', 'unknown')}, file={file.filename}, error={e}",
        )
        raise


@api_router.post("/sessions/multi", response_model=MultiUploadResponse)
async def create_session_multi(
    files: list[UploadFile] = File(...),
    description: str = Form(""),
    file_metadata: str = Form("[]"),
    user: dict = Depends(get_current_user),
):
    """Upload multiple CSV files with per-file type metadata."""
    filenames = [f.filename for f in files]
    try:
        return await s1_upload.handle_multi(files, description, file_metadata_json=file_metadata, user_id=user["id"])
    except HTTPException:
        await notify_gchat(
            "Multi-upload failed",
            f"user={user.get('email', 'unknown')}, files={filenames}",
        )
        raise
    except Exception as e:
        await notify_gchat(
            "Multi-upload failed",
            f"user={user.get('email', 'unknown')}, files={filenames}, error={e}",
        )
        raise


# --- Stage 2: Column Mapping ---

@api_router.post("/sessions/{session_id}/column-mapping", response_model=ColumnMappingResponse)
async def column_mapping(session_id: str, user: dict = Depends(get_current_user)):
    """Run LLM-based column role detection for a session."""
    session = await get_session_with_auth(session_id, user)
    return await s2_column_map.handle(session_id, session)


@api_router.put("/sessions/{session_id}/column-mapping", response_model=ColumnMappingResponse)
async def override_column_mapping(session_id: str, body: ColumnMappingOverride, user: dict = Depends(get_current_user)):
    """Override column mappings with user-provided values."""
    session = await get_session_with_auth(session_id, user)
    return s2_column_map.handle_override(session_id, session, body)


@api_router.post("/sessions/{session_id}/column-mapping/feedback", response_model=ColumnMappingResponse)
async def column_mapping_feedback(session_id: str, body: ColumnMappingFeedback, user: dict = Depends(get_current_user)):
    """Re-run column mapping with user feedback."""
    session = await get_session_with_auth(session_id, user)
    return await s2_column_map.handle_with_feedback(session_id, session, body)


# --- Stage 3: Hypothesis ---

@api_router.post("/sessions/{session_id}/hypothesis", response_model=HypothesisResponse)
async def hypothesis(session_id: str, body: HypothesisRequest = None, user: dict = Depends(get_current_user)):
    """Generate business hypothesis and MCQ questions for a session."""
    session = await get_session_with_auth(session_id, user)
    free_text = body.free_text if body else None
    return await s3_hypothesis.handle(session_id, session, free_text=free_text)


@api_router.post("/sessions/{session_id}/findings/confirm")
async def confirm_findings(session_id: str, body: FindingsConfirmRequest = None, user: dict = Depends(get_current_user)):
    """User confirms computed findings — proceed to training."""
    session = await get_session_with_auth(session_id, user)
    session["findings_confirmed"] = True
    if body and body.additional_context:
        session["additional_context"] = body.additional_context
    store.update(session_id, session)
    return {"status": "confirmed"}


@api_router.post("/sessions/{session_id}/findings/correct")
async def correct_findings(session_id: str, body: MCQAnswers, user: dict = Depends(get_current_user)):
    """User overrides findings via MCQ answers."""
    session = await get_session_with_auth(session_id, user)
    session["mcq_answers"] = body.answers
    session["findings_confirmed"] = True
    store.update(session_id, session)
    return {"status": "corrected"}


@api_router.get("/sessions/{session_id}/cross-file-summary")
async def cross_file_summary(session_id: str, user: dict = Depends(get_current_user)):
    """Get detected data types and cross-file summary."""
    session = await get_session_with_auth(session_id, user)
    return {
        "detected_types": session.get("detected_data_types", [1]),
        "summary": session.get("cross_file_summary", ""),
    }


# --- Stage 4: Features ---

@api_router.post("/sessions/{session_id}/features", response_model=FeaturesResponse)
async def features(session_id: str, body: MCQAnswers, user: dict = Depends(get_current_user)):
    """Compute feature matrix using MCQ answers."""
    session = await get_session_with_auth(session_id, user)
    return await s4_features.handle(session_id, session, body)


# --- Stage 5: Labels ---

@api_router.post("/sessions/{session_id}/labels", response_model=LabelsResponse)
async def labels(session_id: str, user: dict = Depends(get_current_user)):
    """Assign churn labels based on cutoff date."""
    session = await get_session_with_auth(session_id, user)
    return s5_labels.handle(session_id, session)


# --- Stage 6: Train ---

@api_router.post("/sessions/{session_id}/train", response_model=TrainResponse)
async def train(session_id: str, user: dict = Depends(get_current_user)):
    """Train an XGBoost model on labeled features."""
    session = await get_session_with_auth(session_id, user)
    return s6_train.handle(session_id, session)


# --- Stage 7: Results ---

@api_router.get("/sessions/{session_id}/results", response_model=ResultsResponse)
async def results(session_id: str, user: dict = Depends(get_current_user)):
    """Return model results with LLM-generated summary."""
    session = await get_session_with_auth(session_id, user)
    return await s7_results.handle(session_id, session)


# --- Stage 8: Inference ---

@api_router.post("/sessions/{session_id}/inference", response_model=InferenceResponse)
async def inference(session_id: str, user: dict = Depends(get_current_user)):
    """Run churn predictions on all customers."""
    session = await get_session_with_auth(session_id, user)
    return s8_inference.handle(session_id, session)


@api_router.get("/sessions/{session_id}/inference/download")
async def inference_download(session_id: str, user: dict = Depends(get_current_user)):
    """Download churn predictions as a CSV file."""
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
    """Start the agent loop as a background task."""
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
    """Return the agent loop status for a session."""
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
    """Signal the agent loop to stop."""
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
    """Initialize database and set engine on session store."""
    from app.db.engine import init_db, engine
    await init_db()
    store.set_engine(engine)


# Mount static files last (catch-all)
_static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
