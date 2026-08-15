"""Per-IP rate limiting for auth endpoints (CLAUDE.md §47's "safe error
responses" + this audit's finding that login/register had no brute-force
protection at all).

Implemented as a plain FastAPI dependency on top of the `limits` library
directly, rather than slowapi's decorator -- slowapi's `@limiter.limit(...)`
wraps the endpoint in a plain closure whose `__globals__` point at slowapi's
own module, and this codebase uses `from __future__ import annotations`
everywhere, which makes every parameter annotation a lazy string. FastAPI
resolves those strings via `typing.get_type_hints(endpoint)`, which looks the
name up in the *wrapper's* globals, not the route module's -- so it silently
fails to recognize the Pydantic request body model and starts treating it as
a query parameter instead (a documented slowapi+FastAPI+PEP563 interaction).
A bare dependency sidesteps the whole problem: it never wraps the endpoint.

A single process-wide in-memory limiter is sufficient for this app's single-
container deployment. Register/login share one limit: both are guessable-
credential attack surfaces (registration can be used to enumerate taken
emails; login is the classic brute-force target).
"""
from __future__ import annotations

from fastapi import HTTPException, Request, status
from limits import RateLimitItemPerMinute
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter

AUTH_RATE_LIMIT_PER_MINUTE = 10

_storage = MemoryStorage()
_strategy = MovingWindowRateLimiter(_storage)
_auth_limit = RateLimitItemPerMinute(AUTH_RATE_LIMIT_PER_MINUTE)


def reset_rate_limits() -> None:
    """Test-only hook: clears all counters so test order/count never leaks
    between tests (see tests/conftest.py's `client`/`unauthenticated_client`).
    """
    _storage.reset()


def enforce_auth_rate_limit(request: Request) -> None:
    client_key = request.client.host if request.client else "unknown"
    if not _strategy.hit(_auth_limit, client_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please wait a moment and try again.",
        )
