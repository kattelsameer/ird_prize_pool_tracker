"""API-level prize-pool explorer tests (CLAUDE.md §35, §41).

Covers the contract the frontend actually depends on: field names distinct
from the ORM model (category/prize_amount/claim_status, all derived or
renamed -- see app/schemas/prize_pool.py), plus sort/claim_status/pagination
query params, none of which had any test coverage before this file.
"""
import pytest

from tests.data_api_prize_pools import CLAIM_STATUS_CASES, SORT_CASES, build_winner_rows

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


def _seed(db_session):
    from app.core.timeutil import now_kathmandu
    from app.models.prize_pool import PrizePoolWinner

    now = now_kathmandu()
    rows = build_winner_rows(now)
    for row in rows:
        row = dict(row)
        row.pop("name")
        db_session.add(PrizePoolWinner(raw_draw_json={}, source="ird_live", **row))
    db_session.commit()
    return rows


def test_list_prize_pools_returns_the_frontend_facing_contract(client, db_session):
    _seed(db_session)

    response = client.get("/api/prize-pools", params={"limit": 50, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["limit"] == 50
    assert body["offset"] == 0

    item = next(i for i in body["items"] if i["coupon_code"] == "100000000001")
    assert item["category"] == "Bumper Prize"
    assert item["prize_amount"] == 1_000_000
    assert item["prize_amount_net"] == 750_000
    assert item["coupon_code"] == "100000000001"
    assert item["normalized_coupon_code"] == "100000000001"
    assert item["fiscal_year"] == "2083-84"
    assert item["claim_status"] == "CLAIM_ACTIVE"
    assert item["network"] is None


def test_list_prize_pools_pagination_uses_limit_and_offset(client, db_session):
    _seed(db_session)

    first_page = client.get("/api/prize-pools", params={"limit": 2, "offset": 0}).json()
    second_page = client.get("/api/prize-pools", params={"limit": 2, "offset": 2}).json()

    assert first_page["total"] == 3
    assert len(first_page["items"]) == 2
    assert len(second_page["items"]) == 1
    first_ids = {i["id"] for i in first_page["items"]}
    second_ids = {i["id"] for i in second_page["items"]}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.parametrize("name,sort_value,expected_first", SORT_CASES)
def test_list_prize_pools_sort_param(client, db_session, name, sort_value, expected_first):
    _seed(db_session)
    params = {"limit": 50, "offset": 0}
    if sort_value is not None:
        params["sort"] = sort_value

    body = client.get("/api/prize-pools", params=params).json()
    assert body["items"][0]["coupon_code"] == expected_first, name


@pytest.mark.parametrize("name,claim_status_value,expected_coupons", CLAIM_STATUS_CASES)
def test_list_prize_pools_claim_status_filter(client, db_session, name, claim_status_value, expected_coupons):
    _seed(db_session)

    body = client.get(
        "/api/prize-pools", params={"claim_status": claim_status_value, "limit": 50, "offset": 0}
    ).json()
    assert {i["coupon_code"] for i in body["items"]} == expected_coupons, name


def test_get_single_prize_pool_uses_same_contract(client, db_session):
    rows = _seed(db_session)
    listing = client.get("/api/prize-pools", params={"limit": 50, "offset": 0}).json()
    target = next(i for i in listing["items"] if i["coupon_code"] == rows[0]["prize_coupon_number"])

    detail = client.get(f"/api/prize-pools/{target['id']}")
    assert detail.status_code == 200
    assert detail.json()["category"] == "Bumper Prize"


def test_get_single_prize_pool_404(client, db_session):
    response = client.get("/api/prize-pools/does-not-exist")
    assert response.status_code == 404
