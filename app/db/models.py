import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Float, Text, LargeBinary,
    ForeignKey, Index, DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
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
    __tablename__ = "session_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(12), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255))
    profile = Column(JSONB)
    dataframe_blob = Column(LargeBinary)

    session = relationship("Session", back_populates="files")


class AgentRun(Base):
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
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(12), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20))
    content = Column(Text)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    session = relationship("Session", back_populates="chat_messages")
