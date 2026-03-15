"""Session and pipeline state persistence to PostgreSQL."""
import pickle
import zlib
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session, SessionFile, ChatMessage, AgentRun, AgentIteration

logger = logging.getLogger(__name__)

# Keys that map to BYTEA columns (stored as compressed pickle)
BLOB_KEYS = {
    "dataframe": "dataframe_blob",
    "feature_matrix": "feature_matrix_blob",
    "labels": "labels_blob",
    "labeled_features": "labeled_features_blob",
    "model": "model_blob",
    "X_test": "x_test_blob",
    "y_test": "y_test_blob",
    "predictions": "predictions_blob",
}

# Keys that map to JSONB columns
JSONB_KEYS = {
    "profile", "column_mapping", "hypothesis", "mcq_answers",
    "col_map", "tier1_features", "tier2_features", "user_dsl_features",
    "metrics", "confusion_matrix_data", "feature_importance", "feature_names",
}

# Keys that map to scalar columns
SCALAR_KEYS = {
    "name", "filename", "status", "stage", "file_description",
    "free_text", "churn_window_days", "cutoff_date", "training_time_seconds",
}

# Keys that live only in the in-memory dict (not persisted to sessions table)
TRANSIENT_KEYS = {
    "created_at", "dataframes",
}


def serialize_blob(obj: Any) -> bytes:
    """Compress and pickle an object to bytes."""
    return zlib.compress(pickle.dumps(obj, protocol=5))


def deserialize_blob(data: bytes) -> Any:
    """Decompress and unpickle bytes to an object."""
    return pickle.loads(zlib.decompress(data))


def session_dict_to_db_columns(session_dict: dict) -> dict:
    """Convert an in-memory session dict to DB column values."""
    columns = {}
    for key, value in session_dict.items():
        if key in BLOB_KEYS:
            columns[BLOB_KEYS[key]] = serialize_blob(value) if value is not None else None
        elif key in JSONB_KEYS:
            columns[key] = value
        elif key in SCALAR_KEYS:
            columns[key] = value
        # transient keys are skipped
    return columns


def db_row_to_session_dict(row: Session) -> dict:
    """Convert a DB row back to the in-memory session dict format."""
    d = {
        "stage": row.stage or 1,
    }

    # Scalar fields
    for key in SCALAR_KEYS:
        val = getattr(row, key, None)
        if val is not None:
            d[key] = val

    # JSONB fields
    for key in JSONB_KEYS:
        val = getattr(row, key, None)
        if val is not None:
            d[key] = val

    # Blob fields
    for mem_key, col_key in BLOB_KEYS.items():
        blob = getattr(row, col_key, None)
        if blob is not None:
            try:
                d[mem_key] = deserialize_blob(blob)
            except Exception as e:
                logger.warning(f"Failed to deserialize {col_key}: {e}")

    return d


async def save_session(db: AsyncSession, session_id: str, session_dict: dict):
    """Upsert session data to DB."""
    columns = session_dict_to_db_columns(session_dict)
    if not columns:
        return

    result = await db.execute(select(Session).where(Session.id == session_id))
    row = result.scalar_one_or_none()

    if row is None:
        return  # Row must exist (created during store.create)

    for key, value in columns.items():
        setattr(row, key, value)

    await db.commit()


async def load_session(db: AsyncSession, session_id: str) -> dict | None:
    """Load session from DB and return as in-memory dict."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    row = result.scalar_one_or_none()
    if row is None:
        return None
    return db_row_to_session_dict(row)


async def save_chat_message(db: AsyncSession, session_id: str, role: str, content: str, metadata: dict | None = None):
    """Persist a chat message."""
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        metadata_=metadata,
    )
    db.add(msg)
    await db.commit()


async def save_agent_run(db: AsyncSession, session_id: str, agent_state_dict: dict) -> int:
    """Upsert an AgentRun row. Returns the agent_run.id."""
    champion = agent_state_dict.get("champion")
    champion_json = None
    if champion:
        champion_json = {
            "name": champion.get("name"),
            "metrics": champion.get("metrics"),
            "feature_importance": champion.get("feature_importance"),
            "confusion_matrix": champion.get("confusion_matrix"),
            "training_time": champion.get("training_time"),
        }

    # Check for existing run for this session
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.session_id == session_id)
        .order_by(AgentRun.created_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()

    if row is None:
        row = AgentRun(session_id=session_id)
        db.add(row)

    row.status = agent_state_dict.get("status", "completed")
    row.iteration = agent_state_dict.get("iteration", 0)
    row.max_iterations = agent_state_dict.get("max_iterations", 5)
    row.excluded_features = agent_state_dict.get("excluded_features")
    row.dsl_features = agent_state_dict.get("dsl_features")
    row.success_criteria = agent_state_dict.get("success_criteria")
    row.champion = champion_json

    await db.commit()
    await db.refresh(row)
    return row.id


async def save_agent_iteration(db: AsyncSession, agent_run_id: int, iteration_dict: dict):
    """Insert an AgentIteration row."""
    model_results_json = []
    for mr in iteration_dict.get("model_results", []):
        model_results_json.append({
            "name": mr.get("name"),
            "metrics": mr.get("metrics"),
            "feature_importance": mr.get("feature_importance"),
            "confusion_matrix": mr.get("confusion_matrix"),
            "training_time": mr.get("training_time"),
        })

    row = AgentIteration(
        agent_run_id=agent_run_id,
        iteration=iteration_dict.get("iteration"),
        features_used=iteration_dict.get("features_used"),
        features_removed=iteration_dict.get("features_removed"),
        features_added=iteration_dict.get("features_added"),
        model_results=model_results_json,
        evaluation=iteration_dict.get("evaluation"),
    )
    db.add(row)
    await db.commit()


async def load_agent_state(db: AsyncSession, session_id: str) -> dict | None:
    """Load latest AgentRun + AgentIterations and return dict matching AgentState.to_dict() shape."""
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.session_id == session_id)
        .order_by(AgentRun.created_at.desc())
        .limit(1)
    )
    run = result.scalar_one_or_none()
    if run is None:
        return None

    iter_result = await db.execute(
        select(AgentIteration)
        .where(AgentIteration.agent_run_id == run.id)
        .order_by(AgentIteration.iteration)
    )
    iterations = iter_result.scalars().all()

    history = []
    for it in iterations:
        history.append({
            "iteration": it.iteration,
            "features_used": it.features_used or [],
            "features_removed": it.features_removed or [],
            "features_added": it.features_added or [],
            "model_results": it.model_results or [],
            "evaluation": it.evaluation or {},
        })

    return {
        "session_id": session_id,
        "iteration": run.iteration or 0,
        "max_iterations": run.max_iterations or 5,
        "status": run.status or "completed",
        "history": history,
        "champion": run.champion,
    }


async def load_chat_history(db: AsyncSession, session_id: str) -> list[dict]:
    """Load chat history for a session."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    rows = result.scalars().all()
    return [
        {"role": r.role, "content": r.content, "metadata": r.metadata_}
        for r in rows
    ]
