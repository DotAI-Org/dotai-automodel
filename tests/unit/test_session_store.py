import pytest
import time

from app.session_store import SessionStore, TTL_SECONDS


class TestSessionStore:
    def test_create_returns_12_char_hex(self):
        store = SessionStore()
        sid = store.create()
        assert len(sid) == 12
        assert all(c in "0123456789abcdef" for c in sid)

    def test_get_returns_session(self):
        store = SessionStore()
        sid = store.create()
        session = store.get(sid)
        assert session is not None
        assert session["stage"] == 1

    def test_update_merges_data(self):
        store = SessionStore()
        sid = store.create()
        store.update(sid, {"stage": 2, "extra": "value"})
        session = store.get(sid)
        assert session["stage"] == 2
        assert session["extra"] == "value"

    def test_delete_removes_session(self):
        store = SessionStore()
        sid = store.create()
        assert store.delete(sid) is True
        assert store.get(sid) is None

    def test_get_nonexistent_returns_none(self):
        store = SessionStore()
        assert store.get("nonexistent_id") is None

    def test_update_nonexistent_returns_false(self):
        store = SessionStore()
        assert store.update("nonexistent_id", {"key": "val"}) is False

    def test_delete_nonexistent_returns_false(self):
        store = SessionStore()
        assert store.delete("nonexistent_id") is False

    def test_ttl_expiration(self, monkeypatch):
        store = SessionStore()
        sid = store.create()
        # Set created_at to past
        store._sessions[sid]["created_at"] = time.time() - TTL_SECONDS - 1
        assert store.get(sid) is None

    def test_cleanup_expired_removes_stale(self, monkeypatch):
        store = SessionStore()
        sid1 = store.create()
        sid2 = store.create()
        # Make sid1 expired
        store._sessions[sid1]["created_at"] = time.time() - TTL_SECONDS - 1
        store.cleanup_expired()
        assert store.get(sid1) is None
        assert store.get(sid2) is not None
