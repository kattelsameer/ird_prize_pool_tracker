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

    # IMPORTANT: import app.models (not just app.core.db) before create_all.
    # Base.metadata only knows about tables whose model classes have actually
    # been imported/executed at least once; app.core.db.Base itself carries
    # no table definitions on its own. If this fixture is the first thing in
    # the test session to touch the DB, create_all would otherwise run
    # against an empty metadata (creating zero tables), and every query in
    # this test would fail with "no such table: ...".
    from app.core.db import Base
    import app.models  # noqa: F401

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient

    from app.core.db import get_db
    from app.main import app

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
