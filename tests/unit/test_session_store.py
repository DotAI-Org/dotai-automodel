import pytest
import uuid

from app.session_store import SessionStore


class InMemorySessionStore(SessionStore):
    """Test-only session store that operates purely in-memory (no DB)."""

    def create_sync(self, user_id: str = "test_user") -> str:
        session_id = uuid.uuid4().hex[:12]
        self._sessions[session_id] = {
            "stage": 1,
            "user_id": user_id,
        }
        return session_id

    def update(self, session_id: str, data: dict) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.update(data)
        return True

    def delete_sync(self, session_id: str) -> bool:
        if session_id not in self._sessions:
            return False
        del self._sessions[session_id]
        return True


class TestSessionStore:
    def test_create_returns_12_char_hex(self):
        s = InMemorySessionStore()
        sid = s.create_sync()
        assert len(sid) == 12
        assert all(c in "0123456789abcdef" for c in sid)

    def test_get_returns_session(self):
        s = InMemorySessionStore()
        sid = s.create_sync()
        session = s.get(sid)
        assert session is not None
        assert session["stage"] == 1

    def test_update_merges_data(self):
        s = InMemorySessionStore()
        sid = s.create_sync()
        s.update(sid, {"stage": 2, "extra": "value"})
        session = s.get(sid)
        assert session["stage"] == 2
        assert session["extra"] == "value"

    def test_delete_removes_session(self):
        s = InMemorySessionStore()
        sid = s.create_sync()
        assert s.delete_sync(sid) is True
        assert s.get(sid) is None

    def test_get_nonexistent_returns_none(self):
        s = InMemorySessionStore()
        assert s.get("nonexistent_id") is None

    def test_update_nonexistent_returns_false(self):
        s = InMemorySessionStore()
        assert s.update("nonexistent_id", {"key": "val"}) is False

    def test_delete_nonexistent_returns_false(self):
        s = InMemorySessionStore()
        assert s.delete_sync("nonexistent_id") is False
