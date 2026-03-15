"""SQLAlchemy ORM models for users, sessions, agent runs, and chat."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Text, LargeBinary,
    ForeignKey, Index, DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def utcnow():
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """Stores user account data from OAuth providers."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    avatar_url = Column(Text)
    provider = Column(String(20), default="google")
    provider_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=utcnow)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Stores pipeline session state and data blobs."""
    __tablename__ = "sessions"

    id = Column(String(12), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255))
    filename = Column(String(255))
    status = Column(String(20), default="upload")
    stage = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Stage data as JSONB
    profile = Column(JSONB)
    file_description = Column(Text)
    column_mapping = Column(JSONB)
    hypothesis = Column(JSONB)
    free_text = Column(Text)
    mcq_answers = Column(JSONB)
    col_map = Column(JSONB)
    tier1_features = Column(JSONB)
    tier2_features = Column(JSONB)
    user_dsl_features = Column(JSONB)
    churn_window_days = Column(Integer)
    cutoff_date = Column(String(20))

    # Multi-data-type support
    detected_data_types = Column(JSONB)  # [1, 3, 5]
    field_analysis_signature = Column(JSONB)
    churn_window_results = Column(JSONB)
    findings = Column(JSONB)
    findings_confirmed = Column(Integer, default=0)
    feature_tier_map = Column(JSONB)  # {feature_name: tier_number}
    model_comparison = Column(JSONB)  # {model_a: metrics, model_b: metrics, ...}
    lift = Column(JSONB)  # {f1_baseline, f1_enriched, f1_lift}
    tier_attribution = Column(JSONB)  # {tier_1: %, tier_2: %, ...}
    pruning_report = Column(JSONB)
    leakage_report = Column(JSONB)

    # Results
    metrics = Column(JSONB)
    confusion_matrix_data = Column(JSONB)
    feature_importance = Column(JSONB)
    training_time_seconds = Column(Float)
    feature_names = Column(JSONB)

    # Binary blobs (compressed pickle)
    dataframe_blob = Column(LargeBinary)
    feature_matrix_blob = Column(LargeBinary)
    labels_blob = Column(LargeBinary)
    labeled_features_blob = Column(LargeBinary)
    model_blob = Column(LargeBinary)
    x_test_blob = Column(LargeBinary)
    y_test_blob = Column(LargeBinary)
    predictions_blob = Column(LargeBinary)

    user = relationship("User", back_populates="sessions")
    files = relationship("SessionFile", back_populates="session", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_updated_at", "updated_at"),
    )


class SessionFile(Base):
    """Stores per-file data for multi-file uploads."""
    __tablename__ = "session_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(12), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255))
    profile = Column(JSONB)
    dataframe_blob = Column(LargeBinary)
    file_type = Column(String(20), default="transaction")
    user_description = Column(Text)
    connection_description = Column(Text)

    session = relationship("Session", back_populates="files")


class AgentRun(Base):
    """Stores agent loop run state and champion model."""
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(12), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="running")
    iteration = Column(Integer, default=0)
    max_iterations = Column(Integer, default=5)
    excluded_features = Column(JSONB)
    dsl_features = Column(JSONB)
    success_criteria = Column(JSONB)
    champion = Column(JSONB)
    champion_model_blob = Column(LargeBinary)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    session = relationship("Session", back_populates="agent_runs")
    iterations = relationship("AgentIteration", back_populates="agent_run", cascade="all, delete-orphan")


class AgentIteration(Base):
    """Stores per-iteration results within an agent run."""
    __tablename__ = "agent_iterations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    iteration = Column(Integer)
    features_used = Column(JSONB)
    features_removed = Column(JSONB)
    features_added = Column(JSONB)
    model_results = Column(JSONB)
    evaluation = Column(JSONB)

    agent_run = relationship("AgentRun", back_populates="iterations")


class ChatMessage(Base):
    """Stores chat messages between user and agent."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(12), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20))
    content = Column(Text)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    session = relationship("Session", back_populates="chat_messages")
