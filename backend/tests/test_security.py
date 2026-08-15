"""Unit tests for app/core/security.py -- password hashing and JWT helpers.

Pure/dependency-light like test_claim_status.py etc: only needs bcrypt/pyjwt
(already required by requirements.txt for the app itself), not the full
FastAPI/SQLAlchemy stack.
"""
import jwt
import pytest

from tests.data_security import PASSWORD, PASSWORD_OVER_BCRYPT_LIMIT, WRONG_PASSWORD, expired_token_payload


def test_hash_password_roundtrip_verifies_correct_password():
    from app.core.security import hash_password, verify_password

    hashed = hash_password(PASSWORD)
    assert hashed != PASSWORD  # never store plaintext
    assert verify_password(PASSWORD, hashed) is True


def test_verify_password_rejects_wrong_password():
    from app.core.security import hash_password, verify_password

    hashed = hash_password(PASSWORD)
    assert verify_password(WRONG_PASSWORD, hashed) is False


def test_verify_password_fails_closed_on_malformed_hash():
    from app.core.security import verify_password

    assert verify_password(PASSWORD, "not-a-real-bcrypt-hash") is False


def test_hash_password_rejects_passwords_over_bcrypt_byte_limit():
    from app.core.security import hash_password

    with pytest.raises(ValueError):
        hash_password(PASSWORD_OVER_BCRYPT_LIMIT)


def test_create_and_decode_access_token_roundtrip():
    from app.core.security import create_access_token, decode_access_token

    token = create_access_token(user_id="user-123")
    assert decode_access_token(token) == "user-123"


def test_decode_access_token_rejects_garbage():
    from app.core.security import decode_access_token

    assert decode_access_token("not.a.jwt") is None


def test_decode_access_token_rejects_expired_token():
    from app.core.config import get_settings
    from app.core.security import decode_access_token
    from app.core.timeutil import now_kathmandu

    settings = get_settings()
    payload = expired_token_payload(now_kathmandu(), "user-123")
    expired = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    assert decode_access_token(expired) is None


def test_decode_access_token_rejects_token_signed_with_a_different_secret():
    from app.core.security import decode_access_token
    from app.core.timeutil import now_kathmandu

    payload = {"sub": "user-123", "iat": now_kathmandu()}
    forged = jwt.encode(payload, "a-completely-different-secret", algorithm="HS256")

    assert decode_access_token(forged) is None
