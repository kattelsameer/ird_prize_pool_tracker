# Security Review Notes

Reviewed per CLAUDE.md §47 / §10d, using the principal-security-engineer skill's checklist
(secure code review, dependency/supply-chain, and secrets/infra posture lenses). This revision
follows a full project audit (`Audit_01.md`, not committed) that closed every dependency CVE
and the auth rate-limiting gap this document previously carried as a residual risk — those
items are now fixed, not just documented.

## Secure code review (Mode 1)

- **No secrets committed.** `.env.example` files document required env vars with no real
  values; `.gitignore`/`backend/.gitignore` exclude `.env`, `data/*.db`, `data/*.db-journal`,
  `node_modules/`, `__pycache__/`, `dist/`, `.venv/`. Grepped the repo for hardcoded
  API-key/secret/password/token patterns — none found.
- **No PII/PAN/bank data model.** `ConsumerProfile`/`Coupon` intentionally have no
  citizenship/PAN/bank fields — those only matter at in-person claim time and are out of
  this app's data model entirely, per §10d's "do not transmit PAN/bank details" rule taken
  to its logical conclusion (don't even collect them).
- **Data rights implemented** (§10d: view/export/delete personal data): `GET /api/profile/export`
  returns a full JSON bundle of the account's profile and coupons; `DELETE /api/profile`
  cascades user+profile+coupons+notifications+settings in one transaction and is verified
  (both in tests and live against the running Docker containers) to invalidate the account's
  token immediately and free the email for re-registration.
- **CORS** is env-driven (`CORS_ORIGINS`), not wildcarded to `*` with credentials in the
  default config.
- **Error handling**: a global FastAPI exception handler returns a generic message and logs
  full detail server-side only (`app/main.py`) — no stack traces or internals reach the
  client. The `RequestValidationError` handler strips Pydantic's `ctx` field (which can carry
  a raw, non-JSON-serializable exception instance) before serializing.
- **Input validation**: all API inputs go through Pydantic schemas; list endpoints bound
  `limit`/`offset` (e.g. `limit: int = Query(default=50, ge=1, le=200)`) to prevent
  unbounded queries.
- **SQL injection**: all data access goes through SQLAlchemy ORM query construction
  (`repositories/*.py`); no raw string-interpolated SQL anywhere in the codebase.
- **Outbound HTTP (IRD client)**: fixed base URL from config, explicit timeout, capped
  retries with backoff, capped max pages — no unbounded loop, no SSRF vector (URL is not
  user-influenced). A failed sync now also schedules a background retry at 1h/4h/24h
  (CLAUDE.md §10e) rather than only trying again at the next midnight cron or waiting on a
  manual click — capped, never immediate, never indefinite (§39).
- **Logging**: `app/core/logging.py` configures structured logs of operational events only;
  spot-checked `sync_service.py`/`matching_service.py` — they log counts/IDs, not raw PII.
- **Docker**: backend image installs only pinned `requirements.txt` deps; no `--privileged`,
  no host network mode; nginx frontend image serves static files only, proxies `/api/` to
  the backend service by Docker Compose service name (not user-controllable).
- **Authentication**:
  - Passwords are hashed with bcrypt (`app/core/security.py`), never stored or logged in
    plaintext; `hash_password` rejects inputs over bcrypt's 72-byte limit rather than letting
    bcrypt silently truncate them.
  - Login and register both return the exact same generic "Incorrect email or password" /
    account-exists messaging shape regardless of which check failed, to avoid leaking which
    emails have accounts (account-enumeration resistance).
  - `decode_access_token` fails closed on any problem (expired, malformed, wrong signature,
    unknown user) with a single 401 and never distinguishes the reason to the client —
    verified with dedicated tests for each failure mode (`tests/test_security.py`).
  - **Rate limiting** (`app/core/rate_limit.py`): `/api/auth/login` and `/api/auth/register`
    share a 10-requests/minute-per-IP budget, enforced as a plain FastAPI dependency on top of
    the `limits` library. Verified both in tests (trips at exactly the configured threshold)
    and live against the running Docker containers (11 rapid login attempts: the 10th and
    11th return 429). Previously there was no protection here at all.
  - Verified live with two separate real accounts that coupons/notifications/settings never
    leak across accounts (`tests/test_api_auth.py::test_two_accounts_never_see_each_others_coupons`,
    plus a live curl-based check against the running Docker containers).
  - `/api/sync` (trigger) requires authentication.

## Dependency audit (Mode 3) — live, not inspection-only

### Backend (`pip-audit -r backend/requirements.txt`)

**0 known vulnerabilities.** Every previously-tracked finding is resolved:

| Package | Before | After | Resolves |
|---|---|---|---|
| `fastapi` (+ `starlette`) | 0.115.6 (`starlette` 0.41.3) | 0.141.1 (`starlette` 1.6.0) | All 9 starlette advisories (PYSEC-2026-161/248/249/1942/1941/2280/2281) |
| `limits` | — (new) | 5.8.0 | N/A — added for auth rate limiting |

No application-code changes were needed for the FastAPI/Starlette bump beyond what this audit
pass already touched; full backend suite (92 tests) and a fresh `pip-audit` both verified clean.
`python-multipart`, `python-dotenv`, `pytest`, `pydantic-settings` were already patched in an
earlier pass and remain so.

### Frontend (`npm audit`)

**0 known vulnerabilities.**

| Package | Before | After | Resolves |
|---|---|---|---|
| `react-router-dom` (+ `react-router`) | 6.28.0 | 7.18.2 | GHSA-wrjc-x8rr-h8h6 (open redirect), GHSA-337j-9hxr-rhxg (SSR deserialization) |
| `vite` | 5.4.21 | 8.2.1 | GHSA-4w7w-66w2-5vf9 (path traversal in dev-server `.map` handling) + related |
| `vitest` | 2.1.9 | 4.1.10 | GHSA-5xrq-8626-4rwp (arbitrary file read/exec via Vitest UI server) |
| `@vitejs/plugin-react` | 4.3.4 | 6.0.5 | required by the vite 8 bump |

All three were major-version jumps, attempted despite the risk because the app already used
`createBrowserRouter` (react-router's v7-compatible data-router API, so no route
restructuring was needed) and because a plain `npm install` after bumping the versions in
`package.json` resolved the whole tree cleanly with zero config changes. Full frontend suite
(57 tests), typecheck, lint, production build, and both E2E specs all verified green
afterward.

## Secrets & infra posture (Mode 4)

- No hardcoded credentials found (grepped for API key/secret/password/token patterns across
  `backend/app`, `frontend/src`, compose/env files).
- `docker-compose.yml`: no `--privileged`, no host networking, backend/frontend each expose
  only their intended port; SQLite data persisted via a named volume, not a bind mount to an
  arbitrary host path.
- No CI/CD pipeline exists yet in this repo to audit for pipeline-injection/secret-scoping
  issues (out of scope until one is added).

## Residual risks / accepted limitations

1. **`JWT_SECRET` must be changed before any shared/public deployment.** The built-in default
   (`insecure-dev-secret-change-me-before-any-real-deployment`) exists only so `docker compose
   up` works out of the box for local/demo use; `app.main`'s startup logs a loud warning if
   it's still in use. Set a real random value via the `JWT_SECRET` env var first.
2. **No email verification or password reset flow.** Registration accepts any syntactically
   valid email with no confirmation step, and there's no way to recover a lost password short
   of direct database access (or, now, deleting and re-registering the account). Acceptable
   for a personal/local tool; a real deployment would need both before onboarding real users
   who might lose access.
3. **SQLite + no encryption at rest.** Judged acceptable for a single-user-per-account local
   deployment storing no PAN/bank data; add SQLCipher or filesystem-level encryption if the
   host disk isn't trusted. `hashed_password` is bcrypt-hashed regardless, so this specifically
   affects coupon/notification data, not credentials.
4. **General rate limiting**: only `/api/auth/login`/`/api/auth/register` are rate-limited.
   No per-IP rate limiting on the rest of the FastAPI app. Fine for personal local use; add a
   reverse-proxy rate limit (e.g. nginx `limit_req`) in front of the whole API before any
   public exposure.

## Summary

**0 known vulnerabilities** in both `pip-audit` and `npm audit` as of this revision — every
finding from the prior review (starlette, react-router, vite/vitest) is resolved, and the
auth rate-limiting gap previously listed as a residual risk is now closed. Remaining items
above are scope decisions appropriate to a personal/local-use tool, not overlooked gaps.
