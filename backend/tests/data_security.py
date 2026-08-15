"""Scenario tables/builders for test_security.py. No imports of code under test."""
from __future__ import annotations

from datetime import timedelta

PASSWORD = "correct-horse-battery-staple"
WRONG_PASSWORD = "totally-different-password"

# bcrypt silently truncates input beyond 72 bytes; hash_password rejects it instead.
PASSWORD_OVER_BCRYPT_LIMIT = "x" * 73


def expired_token_payload(now, user_id):
    """A JWT payload whose exp is already in the past."""
    return {"sub": user_id, "iat": now - timedelta(hours=1), "exp": now - timedelta(minutes=1)}
