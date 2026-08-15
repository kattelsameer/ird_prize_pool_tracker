"""Shared pytest fixtures for DB/API-level tests.

NOTE: these fixtures require `sqlalchemy` and `fastapi` to be installed (see
requirements.txt). The pure-domain test modules (test_matching.py,
test_claim_status.py, test_nepali_calendar.py, test_normalization.py,
test_ird_adapter.py, test_ird_client.py) do NOT depend on this file or on
sqlalchemy/fastapi at all, by design, so they can run in minimal environments
without any of these fixtures.
"""
from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _configure_test_environment(tmp_path_factory):
    """Point the app at a throwaway sqlite file and disable the live
    scheduler/demo-seeding for the whole test session, before app.main (which
    reads settings at import time) is ever imported.
    """
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["DEMO_MODE"] = "false"
    os.environ["SCHEDULER_ENABLED"] = "false"

    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    # IMPORTANT: import app.models (not just app.core.db) before create_all.
    # Base.metadata only knows about tables whose model classes have actually
    # been imported/executed at least once; app.core.db.Base itself carries
    # no table definitions on its own. If this fixture is the first thing in
    # the test session to touch the DB, create_all would otherwise run
    # against an empty metadata (creating zero tables), and every query in
    # this test would fail with "no such table: ...".
    from app.core.db import Base
    import app.models  # noqa: F401

    # StaticPool is required (not just check_same_thread=False): FastAPI's
    # TestClient runs sync dependencies in a worker thread, and SQLite's
    # default pool for ":memory:" hands each thread its own separate
    # (empty) in-memory database. StaticPool forces every connection to
    # share the single connection that create_all ran against.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


TEST_USER_EMAIL = "test-user@example.com"
TEST_USER_PASSWORD = "test-password-123"


@pytest.fixture()
def client(db_session):
    """Registers a real test account and attaches its access token to every
    request by default, so the existing suite of route tests exercises the
    real auth path end-to-end (not a bypassed dependency override) --
    catching any regression that breaks auth for every protected route, not
    just the dedicated auth tests. Use `unauthenticated_client` instead for
    tests that specifically need to exercise the no-token/invalid-token path.
    """
    from fastapi.testclient import TestClient

    from app.core.db import get_db
    from app.core.rate_limit import reset_rate_limits
    from app.main import app

    # The rate limiter's in-memory storage is process-wide (module-level
    # singleton), not per-TestClient -- without a reset here, ~90 tests each
    # registering/logging in would blow through the 10/minute auth limit well
    # before the suite finishes, failing unrelated tests for reasons that have
    # nothing to do with what they're testing.
    reset_rate_limits()

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        register_response = test_client.post(
            "/api/auth/register",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        token = register_response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def unauthenticated_client(db_session):
    """Same app/DB wiring as `client`, but with no account registered and no
    Authorization header -- for testing the register/login endpoints
    themselves and the no-token/invalid-token 401 paths.
    """
    from fastapi.testclient import TestClient

    from app.core.db import get_db
    from app.core.rate_limit import reset_rate_limits
    from app.main import app

    reset_rate_limits()  # see the matching comment in the `client` fixture above

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
