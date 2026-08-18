"""API-level tests for GET /api/matches/draw-periods (requires fastapi +
sqlalchemy; see test_api_coupons.py's module docstring for why these aren't
exercised in the sandbox this backend was built in)."""
from datetime import date, datetime, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


def _seed_winner(db_session, *, draw_id: str, eligible_from: date, eligible_to: date):
    from app.models.prize_pool import PrizePoolWinner

    winner = PrizePoolWinner(
        source_record_id=f"{draw_id}:some-other-coupon",
        draw_id=draw_id,
        category_title_en="Daily Prize",
        draw_type="GENERAL",
        draw_title_en="Test Draw",
        eligible_from=eligible_from,
        eligible_to=eligible_to,
        published_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
        claim_deadline=datetime(2026, 9, 1, tzinfo=timezone.utc),
        claim_open=True,
        winner_rank=1,
        prize_fiscal_year_code="2083-84",
        # Deliberately NOT the coupon code under test -- this draw is
        # "known"/synced, but the coupon we create below did not win it.
        prize_coupon_number="999999999999",
        normalized_coupon_code="999999999999",
        raw_draw_json={},
    )
    db_session.add(winner)
    db_session.commit()


def test_coupon_inside_a_synced_period_with_no_match_is_drawn(client, db_session):
    _seed_winner(db_session, draw_id="draw-1", eligible_from=date(2026, 8, 1), eligible_to=date(2026, 8, 16))

    created = client.post(
        "/api/coupons",
        json={"coupon_code": "111122223333", "transaction_date": "2026-08-10", "fiscal_year": "2083-84"},
    ).json()

    statuses = client.get("/api/matches/draw-periods").json()
    entry = next(s for s in statuses if s["coupon_id"] == created["id"])
    assert entry["state"] == "DRAWN"
    assert entry["draw_id"] == "draw-1"
    assert entry["eligible_from"] == "2026-08-01"
    assert entry["eligible_to"] == "2026-08-16"
    assert entry["is_estimated"] is False


def test_coupon_newer_than_every_synced_period_is_pending(client, db_session):
    _seed_winner(db_session, draw_id="draw-1", eligible_from=date(2026, 8, 1), eligible_to=date(2026, 8, 16))

    created = client.post(
        "/api/coupons",
        json={"coupon_code": "444455556666", "transaction_date": "2026-08-18", "fiscal_year": "2083-84"},
    ).json()

    statuses = client.get("/api/matches/draw-periods").json()
    entry = next(s for s in statuses if s["coupon_id"] == created["id"])
    assert entry["state"] == "PENDING"
    assert entry["is_estimated"] is True
    assert entry["draw_id"] is None
    assert entry["eligible_from"] == "2026-08-17"
    assert entry["eligible_to"] == "2026-08-31"
    assert entry["estimated_publish_date"] == "2026-09-01"


def test_coupon_with_no_transaction_date_is_omitted(client):
    created = client.post("/api/coupons", json={"coupon_code": "777788889999"}).json()

    statuses = client.get("/api/matches/draw-periods").json()
    coupon_ids = {s["coupon_id"] for s in statuses}
    assert created["id"] not in coupon_ids


def _seed_matching_winner(db_session, *, coupon_code: str, category_title_en: str):
    from app.models.prize_pool import PrizePoolWinner

    winner = PrizePoolWinner(
        source_record_id=f"draw-win:{coupon_code}",
        draw_id="draw-win",
        category_title_en=category_title_en,
        draw_type="GENERAL",
        draw_title_en="Test Draw",
        eligible_from=date(2026, 8, 1),
        eligible_to=date(2026, 8, 16),
        published_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
        claim_deadline=datetime(2026, 9, 1, tzinfo=timezone.utc),
        claim_open=True,
        winner_rank=3,
        prize_fiscal_year_code="2083-84",
        prize_coupon_number=coupon_code,
        normalized_coupon_code=coupon_code,
        raw_draw_json={},
    )
    db_session.add(winner)
    db_session.commit()


def test_match_includes_prize_amount_and_eligible_period(client, db_session):
    _seed_matching_winner(db_session, coupon_code="123412341234", category_title_en="Daily Prize")
    client.post(
        "/api/coupons",
        json={"coupon_code": "123412341234", "transaction_date": "2026-08-05", "fiscal_year": "2083-84"},
    )

    matches = client.get("/api/matches").json()
    assert len(matches) == 1
    match = matches[0]
    assert match["prize_amount"] == 133_334
    assert match["prize_amount_net"] == 100_000
    assert match["winner_rank"] == 3
    assert match["eligible_from"] == "2026-08-01"
    assert match["eligible_to"] == "2026-08-16"


def test_match_prize_amount_is_null_for_an_unknown_category(client, db_session):
    _seed_matching_winner(db_session, coupon_code="567856785678", category_title_en="Mystery Prize")
    client.post(
        "/api/coupons",
        json={"coupon_code": "567856785678", "transaction_date": "2026-08-05", "fiscal_year": "2083-84"},
    )

    matches = client.get("/api/matches").json()
    assert len(matches) == 1
    assert matches[0]["prize_amount"] is None
    assert matches[0]["prize_amount_net"] is None
