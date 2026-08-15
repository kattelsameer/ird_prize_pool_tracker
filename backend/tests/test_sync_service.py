"""Sync-service DB-integration tests (requires fastapi + sqlalchemy installed).

Not executed in the sandbox this backend was built in (see final report /
requirements.txt deviation note). The HTTP layer is mocked via
httpx.MockTransport (same technique proven to work for real in
test_ird_client.py) rather than hitting the live network, per CLAUDE.md §54.
"""
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

import httpx  # noqa: E402

from tests.data_sync_service import INITIAL_SYNC_PAGE, UPDATED_SYNC_PAGE  # noqa: E402


def _patched_ird_client(handler):
    """Return a context manager patching app.services.sync_service.IrdClient
    so run_sync() uses a mocked transport instead of the live network."""
    from app.integrations.ird.ird_client import IrdClient, IrdClientConfig

    def factory(config: IrdClientConfig | None = None):
        return IrdClient(config=config, transport=httpx.MockTransport(handler))

    return patch("app.services.sync_service.IrdClient", side_effect=factory)


def _handler_for(payload):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return handler


def test_successful_sync_inserts_winners_and_records_success(db_session):
    from app.models.prize_pool import PrizePoolWinner
    from app.services import sync_service

    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        run_id = sync_service.run_sync(db_session)

    from app.repositories.sync_repo import get_latest_sync_run

    run = get_latest_sync_run(db_session)
    assert run.id == run_id
    assert run.status == "success"
    assert run.records_inserted == 2
    assert run.records_updated == 0

    rows = db_session.query(PrizePoolWinner).all()
    assert len(rows) == 2


def test_idempotent_repeated_sync_produces_no_duplicate_rows(db_session):
    from app.models.prize_pool import PrizePoolWinner
    from app.services import sync_service

    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        sync_service.run_sync(db_session)
        sync_service.run_sync(db_session)

    rows = db_session.query(PrizePoolWinner).all()
    assert len(rows) == 2  # not 4

    from app.repositories.sync_repo import get_latest_sync_run

    second_run = get_latest_sync_run(db_session)
    assert second_run.records_inserted == 0
    assert second_run.records_updated == 2


def test_government_record_update_flips_claim_open(db_session):
    from app.models.prize_pool import PrizePoolWinner
    from app.services import sync_service

    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        sync_service.run_sync(db_session)

    with _patched_ird_client(_handler_for(UPDATED_SYNC_PAGE)):
        sync_service.run_sync(db_session)

    rows = db_session.query(PrizePoolWinner).all()
    assert len(rows) == 2
    assert all(row.claim_open is False for row in rows)


def test_sync_failure_preserves_existing_data(db_session):
    from app.models.prize_pool import PrizePoolWinner
    from app.services import sync_service

    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        sync_service.run_sync(db_session)

    def failing_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated outage", request=request)

    with _patched_ird_client(failing_handler):
        run_id = sync_service.run_sync(db_session)

    from app.repositories.sync_repo import get_latest_sync_run

    run = get_latest_sync_run(db_session)
    assert run.id == run_id
    assert run.status == "failed"
    assert run.error_message

    # Existing data from the first successful sync must still be present.
    rows = db_session.query(PrizePoolWinner).all()
    assert len(rows) == 2


def test_new_match_generates_notification(db_session):
    from app.models.notification import Notification
    from app.repositories.coupon_repo import create_coupon
    from app.repositories.profile_repo import get_or_create_profile_for_user
    from app.repositories.user_repo import create_user
    from app.services import sync_service

    user = create_user(db_session, email="sync-test@example.com", password="test-password-123")
    profile = get_or_create_profile_for_user(db_session, user.id)
    create_coupon(
        db_session,
        profile_id=profile.id,
        coupon_code="300000000001",
        transaction_date=None,
        fiscal_year="2083-84",
        network=None,
    )

    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        sync_service.run_sync(db_session)

    notifications = db_session.query(Notification).filter_by(type="NEW_MATCH").all()
    assert len(notifications) == 1

    # Re-syncing the exact same data must not create a second NEW_MATCH
    # notification for the same coupon/draw pair (CLAUDE.md §33 dedup rule).
    with _patched_ird_client(_handler_for(INITIAL_SYNC_PAGE)):
        sync_service.run_sync(db_session)

    notifications_after = db_session.query(Notification).filter_by(type="NEW_MATCH").all()
    assert len(notifications_after) == 1
