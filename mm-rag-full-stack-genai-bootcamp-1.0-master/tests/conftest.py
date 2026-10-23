"""Shared pytest fixtures for the MM-RAG test suite.

These tests are self-contained: they run against an in-memory SQLite
database and mock the Celery enqueue + LLM generator, so they need no
PostgreSQL, Redis, Qdrant, or Ollama. Tests that require the real stack
should be marked ``@pytest.mark.integration``.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------
# Deterministic, isolated configuration.
#
# These MUST be set before importing any backend module: backend.auth
# resolves JWT_SECRET_KEY at import time, backend.storage reads
# STORAGE_BACKEND, and backend.observability reads METRICS_FILE.
# ---------------------------------------------------------------------

os.environ["JWT_SECRET_KEY"] = (
    "test-only-secret-key-0123456789abcdefghijklmnop"
)
os.environ["STORAGE_BACKEND"] = "local"
os.environ["STORAGE_ROOT"] = tempfile.mkdtemp(prefix="mmrag-test-storage-")
os.environ["METRICS_FILE"] = str(
    Path(tempfile.mkdtemp(prefix="mmrag-test-metrics-"))
    / "observability.json"
)

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from backend.database import Base  # noqa: E402


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: requires the real stack (PostgreSQL/Redis/Qdrant/Ollama)",
    )


# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------


@pytest.fixture()
def engine():
    """A fresh in-memory SQLite engine per test."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    yield session
    session.close()


# ---------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------


@pytest.fixture()
def client(engine, session_factory, monkeypatch):
    """TestClient bound to the isolated SQLite database."""
    from fastapi.testclient import TestClient

    from backend import main as main_module
    from backend.database import get_db

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    main_module.app.dependency_overrides[get_db] = override_get_db

    # Never touch Redis/Celery from tests. The enqueue is a no-op; the
    # worker's own behaviour is covered by the job-status tests.
    monkeypatch.setattr(
        main_module.ingest_document,
        "apply_async",
        lambda *args, **kwargs: None,
    )

    with TestClient(main_module.app) as test_client:
        yield test_client

    main_module.app.dependency_overrides.clear()


# ---------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------

DEFAULT_PASSWORD = "password123"


@pytest.fixture()
def auth_headers(client):
    """Register + log in a user, returning ready-to-use auth headers."""

    def _headers(
        email: str = "user@example.com",
        password: str = DEFAULT_PASSWORD,
    ) -> dict[str, str]:
        client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
        response = client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture()
def pdf_bytes():
    """A minimal, valid one-page PDF generated in memory."""
    import fitz

    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Service agreement between Acme Ltd and Globex for 2026.",
    )
    data = document.tobytes()
    document.close()
    return data
