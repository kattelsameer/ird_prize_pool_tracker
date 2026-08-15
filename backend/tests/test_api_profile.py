"""API-level profile tests: view/edit (CLAUDE.md §23), export/delete data
rights (CLAUDE.md §10d). No coverage existed for this router before this
audit -- the export/delete endpoints and the frontend UI that uses them were
both newly added.
"""
import pytest

from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD
from tests.data_api_profile import UPDATE_PROFILE_CASES

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


def test_get_profile_returns_default_display_name(client):
    response = client.get("/api/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] is None
    assert set(body.keys()) == {"id", "display_name", "created_at", "updated_at"}


@pytest.mark.parametrize("name,payload,expected", UPDATE_PROFILE_CASES)
def test_put_profile_updates_display_name(client, name, payload, expected):
    response = client.put("/api/profile", json=payload)
    assert response.status_code == 200, name
    assert response.json()["display_name"] == expected, name


def test_profile_requires_auth(unauthenticated_client):
    response = unauthenticated_client.get("/api/profile")
    assert response.status_code == 401


def test_export_bundle_contains_account_email_profile_and_coupons(client):
    client.post(
        "/api/coupons",
        json={"coupon_code": "007315254493", "fiscal_year": "2083-84"},
    )

    response = client.get("/api/profile/export")
    assert response.status_code == 200
    body = response.json()

    assert body["account_email"] == TEST_USER_EMAIL
    assert "exported_at" in body
    assert body["profile"]["id"]
    assert len(body["coupons"]) == 1
    assert body["coupons"][0]["coupon_code"] == "007315254493"


def test_export_requires_auth(unauthenticated_client):
    response = unauthenticated_client.get("/api/profile/export")
    assert response.status_code == 401


def test_delete_account_removes_all_data_and_login_no_longer_works(client, unauthenticated_client):
    client.post("/api/coupons", json={"coupon_code": "111111111111"})

    delete_response = client.delete("/api/profile")
    assert delete_response.status_code == 204

    # The token from before deletion is now dangling -- the user row it
    # pointed at no longer exists, so it must be rejected, not silently
    # treated as still authenticated.
    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 401

    # The email is free again: a fresh registration with the same address
    # must succeed rather than 409-conflicting against a "deleted" ghost row.
    re_register = unauthenticated_client.post(
        "/api/auth/register",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert re_register.status_code == 201


def test_delete_account_requires_auth(unauthenticated_client):
    response = unauthenticated_client.delete("/api/profile")
    assert response.status_code == 401
