"""API-level coupon CRUD tests (requires fastapi + sqlalchemy installed).

Not executed in the sandbox this backend was built in (see final report /
requirements.txt deviation note for why) -- written and structured to run
cleanly once `pip install -r requirements.txt` succeeds in an environment with
package-registry access.
"""
from datetime import date, datetime, timezone

import pytest

from tests.data_api_coupons import (
    CREATE_COUPON_CASES,
    DUPLICATE_COUPON_PAYLOAD,
    EXISTING_WINNER_COUPON_CODE,
    EXISTING_WINNER_DRAW_ID,
    MATCHING_COUPON_PAYLOAD,
)

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


def test_create_coupon_cases(client):
    for name, payload, expected_status in CREATE_COUPON_CASES:
        response = client.post("/api/coupons", json=payload)
        assert response.status_code == expected_status, f"{name}: {response.text}"
        if expected_status == 201:
            body = response.json()
            assert body["coupon_code"] == payload["coupon_code"]
            assert body["normalized_coupon_code"]
            assert body["id"]


def test_duplicate_coupon_entry_is_allowed_and_produces_two_rows(client):
    r1 = client.post("/api/coupons", json=DUPLICATE_COUPON_PAYLOAD)
    r2 = client.post("/api/coupons", json=DUPLICATE_COUPON_PAYLOAD)
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] != r2.json()["id"]

    listing = client.get("/api/coupons", params={"search": "222233334444"})
    assert listing.status_code == 200
    assert listing.json()["total"] == 2


def test_get_update_delete_lifecycle(client):
    created = client.post("/api/coupons", json={"coupon_code": "555566667777"}).json()
    coupon_id = created["id"]

    fetched = client.get(f"/api/coupons/{coupon_id}")
    assert fetched.status_code == 200
    assert fetched.json()["coupon_code"] == "555566667777"

    updated = client.put(f"/api/coupons/{coupon_id}", json={"fiscal_year": "2083-84"})
    assert updated.status_code == 200
    assert updated.json()["fiscal_year"] == "2083-84"

    deleted = client.delete(f"/api/coupons/{coupon_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/coupons/{coupon_id}")
    assert missing.status_code == 404


def test_creating_a_coupon_that_matches_an_existing_winner_notifies_immediately(client, db_session):
    from app.models.prize_pool import PrizePoolWinner

    winner = PrizePoolWinner(
        source_record_id="test-source-existing-winner",
        draw_id=EXISTING_WINNER_DRAW_ID,
        category_title_en="Daily Prize",
        draw_type="GENERAL",
        draw_title_en="Test Draw",
        eligible_from=date(2026, 7, 17),
        eligible_to=date(2026, 7, 31),
        published_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
        claim_deadline=datetime(2026, 8, 22, tzinfo=timezone.utc),
        claim_open=True,
        winner_rank=1,
        prize_fiscal_year_code="2083-84",
        prize_coupon_number=EXISTING_WINNER_COUPON_CODE,
        normalized_coupon_code=EXISTING_WINNER_COUPON_CODE,
        raw_draw_json={},
    )
    db_session.add(winner)
    db_session.commit()

    response = client.post("/api/coupons", json=MATCHING_COUPON_PAYLOAD)
    assert response.status_code == 201

    notifications = client.get("/api/notifications").json()["items"]
    assert any(n["type"] == "NEW_MATCH" for n in notifications), notifications

    # Re-fetching (idempotency check) must not create a second NEW_MATCH notification.
    again = client.get("/api/wins")
    assert again.status_code == 200
    notifications_after = client.get("/api/notifications").json()["items"]
    new_match_count = sum(1 for n in notifications_after if n["type"] == "NEW_MATCH")
    assert new_match_count == 1


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
