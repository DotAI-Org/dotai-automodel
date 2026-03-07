import uuid
import asyncio
import logging
from typing import Any
from datetime import datetime, timezone

from sqlalchemy import select, delete

logger = logging.getLogger(__name__)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, dict[str, Any]] = {}
        self._engine = None

    def set_engine(self, engine):
        self._engine = engine

    async def create(self, user_id: str) -> str:
        from app.db.engine import AsyncSessionLocal
        from app.db.models import Session

        session_id = uuid.uuid4().hex[:12]

        async with AsyncSessionLocal() as db:
            row = Session(
                id=session_id,
                user_id=user_id,
                stage=1,
            )
            db.add(row)
            await db.commit()

        self._sessions[session_id] = {
            "stage": 1,
            "user_id": str(user_id),
        }
        return session_id

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    async def get_or_load(self, session_id: str) -> dict[str, Any] | None:
        """Check cache first, fall back to DB."""
        cached = self._sessions.get(session_id)
        if cached is not None:
            return cached

        from app.db.engine import AsyncSessionLocal
        from app.persistence import load_session

        async with AsyncSessionLocal() as db:
            data = await load_session(db, session_id)
            if data is not None:
                self._sessions[session_id] = data
            return data

    def update(self, session_id: str, data: dict[str, Any]) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.update(data)
        # Schedule async persist
        asyncio.ensure_future(self._persist(session_id))
        return True

    async def _persist(self, session_id: str):
        session = self._sessions.get(session_id)
        if session is None:
            return
        try:
            from app.db.engine import AsyncSessionLocal
            from app.persistence import save_session

            async with AsyncSessionLocal() as db:
                await save_session(db, session_id, session)
        except Exception as e:
            logger.error(f"Failed to persist session {session_id}: {e}")

    async def delete(self, session_id: str) -> bool:
        self._sessions.pop(session_id, None)

        from app.db.engine import AsyncSessionLocal
        from app.db.models import Session

        async with AsyncSessionLocal() as db:
            await db.execute(delete(Session).where(Session.id == session_id))
            await db.commit()
        return True

    async def list_sessions(self, user_id: str) -> list[dict]:
        from app.db.engine import AsyncSessionLocal
        from app.db.models import Session

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(
                    Session.id,
                    Session.name,
                    Session.filename,
                    Session.status,
                    Session.stage,
                    Session.created_at,
                    Session.updated_at,
                    Session.metrics,
                )
                .where(Session.user_id == user_id)
                .order_by(Session.updated_at.desc())
            )
            rows = result.all()
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "filename": r.filename,
                    "status": r.status or "upload",
                    "stage": r.stage or 1,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                    "metrics": r.metrics,
                }
                for r in rows
            ]

    async def rename(self, session_id: str, name: str):
        from app.db.engine import AsyncSessionLocal
        from app.db.models import Session

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Session).where(Session.id == session_id))
            row = result.scalar_one_or_none()
            if row:
                row.name = name
                await db.commit()

        cached = self._sessions.get(session_id)
        if cached:
            cached["name"] = name

    async def get_owner(self, session_id: str) -> str | None:
        """Get the user_id that owns this session."""
        cached = self._sessions.get(session_id)
        if cached and "user_id" in cached:
            return cached["user_id"]

        from app.db.engine import AsyncSessionLocal
        from app.db.models import Session

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Session.user_id).where(Session.id == session_id)
            )
            row = result.scalar_one_or_none()
            return str(row) if row else None


store = SessionStore()
