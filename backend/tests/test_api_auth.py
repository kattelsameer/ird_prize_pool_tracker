"""API-level authentication tests: register, login, and the protected-route
401 paths. Uses `unauthenticated_client` (no account, no Authorization header)
rather than the default `client` fixture, which auto-registers an account --
these tests need to control that registration/login themselves.
"""
import pytest

from tests.data_api_auth import LOGIN_CASES, REGISTER_CASES, UNKNOWN_EMAIL_LOGIN, VALID_EMAIL, VALID_PASSWORD

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")


@pytest.mark.parametrize("name,payload,expected_status", REGISTER_CASES)
def test_register_cases(unauthenticated_client, name, payload, expected_status):
    response = unauthenticated_client.post("/api/auth/register", json=payload)
    assert response.status_code == expected_status, f"{name}: {response.text}"
    if expected_status == 201:
        body = response.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == payload["email"]
        assert "password" not in body["user"]
        assert "hashed_password" not in body["user"]


def test_register_duplicate_email_rejected(unauthenticated_client):
    payload = {"email": VALID_EMAIL, "password": VALID_PASSWORD}
    first = unauthenticated_client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = unauthenticated_client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_register_email_is_case_and_whitespace_normalized_for_uniqueness(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register", json={"email": VALID_EMAIL, "password": VALID_PASSWORD}
    )
    variant = unauthenticated_client.post(
        "/api/auth/register",
        json={"email": f"  {VALID_EMAIL.upper()}  ", "password": VALID_PASSWORD},
    )
    assert variant.status_code == 409


@pytest.mark.parametrize("name,login_overrides,expected_status", LOGIN_CASES)
def test_login_cases(unauthenticated_client, name, login_overrides, expected_status):
    unauthenticated_client.post(
        "/api/auth/register", json={"email": VALID_EMAIL, "password": VALID_PASSWORD}
    )
    response = unauthenticated_client.post(
        "/api/auth/login", json={"email": VALID_EMAIL, **login_overrides}
    )
    assert response.status_code == expected_status, f"{name}: {response.text}"
    if expected_status == 200:
        assert response.json()["access_token"]


def test_login_unknown_email_rejected(unauthenticated_client):
    response = unauthenticated_client.post("/api/auth/login", json=UNKNOWN_EMAIL_LOGIN)
    assert response.status_code == 401


def test_me_returns_current_user_with_a_valid_token(unauthenticated_client):
    register = unauthenticated_client.post(
        "/api/auth/register", json={"email": VALID_EMAIL, "password": VALID_PASSWORD}
    )
    token = register.json()["access_token"]

    response = unauthenticated_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == VALID_EMAIL


def test_protected_route_without_token_is_401(unauthenticated_client):
    response = unauthenticated_client.get("/api/coupons")
    assert response.status_code == 401


def test_protected_route_with_garbage_token_is_401(unauthenticated_client):
    response = unauthenticated_client.get(
        "/api/coupons", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_two_accounts_never_see_each_others_coupons(unauthenticated_client):
    user_a = unauthenticated_client.post(
        "/api/auth/register", json={"email": "user-a@example.com", "password": VALID_PASSWORD}
    ).json()
    user_b = unauthenticated_client.post(
        "/api/auth/register", json={"email": "user-b@example.com", "password": VALID_PASSWORD}
    ).json()

    unauthenticated_client.post(
        "/api/coupons",
        json={"coupon_code": "111111111111"},
        headers={"Authorization": f"Bearer {user_a['access_token']}"},
    )

    b_coupons = unauthenticated_client.get(
        "/api/coupons", headers={"Authorization": f"Bearer {user_b['access_token']}"}
    ).json()
    assert b_coupons["total"] == 0

    a_coupons = unauthenticated_client.get(
        "/api/coupons", headers={"Authorization": f"Bearer {user_a['access_token']}"}
    ).json()
    assert a_coupons["total"] == 1
