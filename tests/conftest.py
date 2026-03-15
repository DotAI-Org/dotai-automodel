import os
import sys
import uuid
import pytest
import pandas as pd
import numpy as np

# Ensure churn-tool root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.session_store import store, SessionStore
from app.stages import s4_features, s5_labels, s6_train


# --------------- Test Store Helpers ---------------

def _create_test_session(session_store: SessionStore, user_id: str = "test_user") -> str:
    """Create a session in-memory without DB (for unit tests)."""
    session_id = uuid.uuid4().hex[:12]
    session_store._sessions[session_id] = {
        "stage": 1,
        "user_id": user_id,
    }
    return session_id


# Monkey-patch the module-level store.update to skip async persist in tests
_original_update = store.update.__func__ if hasattr(store.update, '__func__') else None


def _sync_update(self, session_id: str, data: dict) -> bool:
    """Sync update that skips asyncio.ensure_future DB persist."""
    session = self._sessions.get(session_id)
    if session is None:
        return False
    session.update(data)
    return True


# Apply the sync patch to the module-level store
store.update = _sync_update.__get__(store, SessionStore)


# --------------- Markers ---------------

def pytest_configure(config):
    config.addinivalue_line("markers", "llm: tests requiring GEMINI_API_KEY")
    config.addinivalue_line("markers", "slow: tests taking > 10 seconds")


@pytest.fixture(autouse=True)
def _skip_llm_if_no_key(request):
    if request.node.get_closest_marker("llm"):
        if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GROQ_API_KEY"):
            pytest.skip("GEMINI_API_KEY or GROQ_API_KEY not set")


# --------------- Data Fixtures ---------------

@pytest.fixture
def sample_ecommerce_df():
    path = os.path.join(os.path.dirname(__file__), "test_data", "ecommerce_sample.csv")
    return pd.read_csv(path)


@pytest.fixture
def sample_maturity_df():
    path = os.path.join(os.path.dirname(__file__), "test_data", "maturity_churn.csv")
    return pd.read_csv(path)


@pytest.fixture
def ecommerce_col_map():
    return {
        "customer_id": "customer_id",
        "transaction_date": "transaction_date",
        "amount": "amount",
        "product": "product",
        "quantity": "quantity",
        "category": "category",
        "channel": "channel",
        "region": "region",
    }


@pytest.fixture
def maturity_col_map():
    return {
        "customer_id": "customer_id",
        "transaction_date": "transaction_date",
        "amount": "amount",
        "product": "product",
    }


# --------------- Computed Fixtures ---------------

@pytest.fixture
def ecommerce_feature_matrix(sample_ecommerce_df, ecommerce_col_map):
    df = sample_ecommerce_df
    col_map = ecommerce_col_map
    feature_matrix = pd.DataFrame()
    for name, func in s4_features.TIER1_FEATURES.items():
        try:
            feature_matrix[name] = func(df, col_map)
        except Exception:
            continue
    return feature_matrix


@pytest.fixture
def ecommerce_labels(sample_ecommerce_df, ecommerce_col_map, ecommerce_feature_matrix):
    sid = _create_test_session(store)
    store.update(sid, {
        "dataframe": sample_ecommerce_df,
        "col_map": ecommerce_col_map,
        "feature_matrix": ecommerce_feature_matrix,
        "mcq_answers": {},
    })
    session = store.get(sid)
    s5_labels.handle(sid, session)
    session = store.get(sid)
    return session["labels"]


@pytest.fixture
def trained_session(sample_ecommerce_df, ecommerce_col_map, ecommerce_feature_matrix):
    sid = _create_test_session(store)
    store.update(sid, {
        "dataframe": sample_ecommerce_df,
        "col_map": ecommerce_col_map,
        "feature_matrix": ecommerce_feature_matrix,
        "mcq_answers": {},
    })
    session = store.get(sid)
    s5_labels.handle(sid, session)
    session = store.get(sid)
    s6_train.handle(sid, session)
    session = store.get(sid)
    return session, sid, store


# --------------- Session Fixture ---------------

@pytest.fixture
def fresh_store():
    return SessionStore()
