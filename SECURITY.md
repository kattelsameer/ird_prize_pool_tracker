# Security Review Notes

Reviewed per CLAUDE.md §47 / §10d, using the principal-security-engineer skill's checklist
(secure code review, dependency/supply-chain, and secrets/infra posture lenses). This revision
adds a live dependency audit (`npm audit`, `pip-audit`) — an earlier pass of this document
could only review pinned versions by inspection, since that sandbox had no package-registry
access; this environment does, so real CVE data replaces that caveat below.

## Secure code review (Mode 1)

- **No secrets committed.** `.env.example` files document required env vars with no real
  values; `.gitignore`/`backend/.gitignore` exclude `.env`, `data/*.db`, `data/*.db-journal`,
  `node_modules/`, `__pycache__/`, `dist/`, `.venv/`. Grepped the repo for hardcoded
  API-key/secret/password/token patterns — none found.
- **No PII/PAN/bank data model.** `ConsumerProfile`/`Coupon` intentionally have no
  citizenship/PAN/bank fields — those only matter at in-person claim time and are out of
  this app's data model entirely, per §10d's "do not transmit PAN/bank details" rule taken
  to its logical conclusion (don't even collect them).
- **CORS** is env-driven (`CORS_ORIGINS`), not wildcarded to `*` with credentials in the
  default config.
- **Error handling**: a global FastAPI exception handler returns a generic message and logs
  full detail server-side only (`app/main.py`) — no stack traces or internals reach the
  client. The `RequestValidationError` handler strips Pydantic's `ctx` field (which can carry
  a raw, non-JSON-serializable exception instance) before serializing — this was a real bug
  fixed this session (see git log), not merely a defensive habit.
- **Input validation**: all API inputs go through Pydantic schemas; list endpoints bound
  `limit`/`offset` (e.g. `limit: int = Query(default=50, ge=1, le=200)`) to prevent
  unbounded queries.
- **SQL injection**: all data access goes through SQLAlchemy ORM query construction
  (`repositories/*.py`); no raw string-interpolated SQL anywhere in the codebase.
- **Outbound HTTP (IRD client)**: fixed base URL from config, explicit timeout, capped
  retries with backoff, capped max pages — no unbounded loop, no SSRF vector (URL is not
  user-influenced).
- **Logging**: `app/core/logging.py` configures structured logs of operational events only;
  spot-checked `sync_service.py`/`matching_service.py` — they log counts/IDs, not raw PII.
- **Docker**: backend image installs only pinned `requirements.txt` deps; no `--privileged`,
  no host network mode; nginx frontend image serves static files only, proxies `/api/` to
  the backend service by Docker Compose service name (not user-controllable).
- **Authentication** (added this revision, replacing the earlier no-auth design):
  - Passwords are hashed with bcrypt (`app/core/security.py`), never stored or logged in
    plaintext; `hash_password` rejects inputs over bcrypt's 72-byte limit rather than letting
    bcrypt silently truncate them.
  - Login and register both return the exact same generic "Incorrect email or password" /
    account-exists messaging shape regardless of which check failed, to avoid leaking which
    emails have accounts (account-enumeration resistance).
  - `decode_access_token` fails closed on any problem (expired, malformed, wrong signature,
    unknown user) with a single 401 and never distinguishes the reason to the client —
    verified with dedicated tests for each failure mode (`tests/test_security.py`).
  - Verified live with two separate real accounts that coupons/notifications/settings never
    leak across accounts (`tests/test_api_auth.py::test_two_accounts_never_see_each_others_coupons`,
    plus a live curl-based check against the running Docker containers).
  - `/api/sync` (trigger) now requires authentication too — previously anyone could trigger a
    sync against the live IRD API with no rate limit at all (CLAUDE.md §39's "do not hammer
    the government service" had no enforcement behind it whatsoever).

## Dependency audit (Mode 3) — live, not inspection-only

### Backend (`pip-audit -r backend/requirements.txt`)

Applied, verified against the full test suite (76 passed) and a Docker rebuild:

| Package | Before | After | Advisory |
|---|---|---|---|
| `pydantic-settings` | 2.14.0 | 2.14.2 | GHSA-4xgf-cpjx-pc3j (symlink path traversal in `NestedSecretsSettingsSource`) — this app never sets `secrets_dir`, so unreachable regardless; patched anyway |
| `python-multipart` | 0.0.20 | 0.0.31 | 6 advisories (path traversal, DoS, `;`-separator param smuggling) — this app has no `Form()`/`UploadFile` routes (all JSON bodies via Pydantic), so unreachable regardless; patched anyway |
| `python-dotenv` | 1.0.1 | 1.2.2 | PYSEC-2026-2270 |
| `pytest` | 8.3.4 | 9.0.3 | PYSEC-2026-1845 (dev-only; verified `pytest-cov`/`respx` still work — full suite green) |

**Deferred, documented (not silently ignored): `starlette` 0.41.3 — 9 advisories**, the two
most severe being:

- **CVE-2025-62727 (High, 7.5)** — O(n²) `Range`-header parsing DoS via `FileResponse`/
  `StaticFiles`. **Not reachable in this app**: grepped the backend for `StaticFiles`/
  `FileResponse` — zero usages. The frontend's static files are served by nginx, not FastAPI.
- **CVE-2026-48710 (Moderate, 6.5)** — malformed `Host` header can desync `request.url.path`
  from the actual routed path, defeating middleware that makes security decisions from
  `request.url`. **Not reachable in this app**: the only middleware registered is CORS; no
  custom path-based access control reads `request.url.path`.

Fixing any of these requires `starlette>=0.47.2` (up to `1.1.0`/`1.3.1` for the others), but
`fastapi==0.115.6` pins `starlette>=0.40.0,<0.42.0` — there is no in-range patched version.
**The real fix is a coordinated FastAPI + Starlette major-version upgrade** (FastAPI's own
current release allows `starlette>=0.46.0`, no upper cap), which needs its own dedicated
regression pass (the app still uses the now-deprecated `@app.on_event` lifecycle hooks,
among other things likely to need touching) rather than a blind version bump under time
pressure. **Recommended as the next follow-up work item**, not deferred indefinitely.

### Frontend (`npm audit`)

| Package | Before | After | Advisory |
|---|---|---|---|
| `react-router-dom` (+ `react-router`) | 6.28.0 | 6.30.4 | Partial — see below |

**Correction to an earlier assumption in this same session**: `npm audit fix` reported
`react-router-dom`'s fix as available without a breaking change, but that only bumped the
patch release within the declared `^6.28.0` range. The actual advisory this app is still
exposed to, **GHSA-wrjc-x8rr-h8h6 (Moderate) — open redirect via backslash in `<Link>`/
`useNavigate`** — is fixed only in `react-router` **7.18.0+**, a major-version jump with real
breaking changes (data routers, loader/action APIs). Deferred for the same reason as
FastAPI/Starlette above: needs a dedicated migration + regression pass, not a blind bump.
Real-world exposure here is low (exploiting an open redirect needs the app to render a
`<Link>`/navigate to an attacker-controlled path, which no code in this app does — all
`to=`/`navigate()` targets are internal, static routes), but it's a real, unresolved
advisory, not something to claim as fixed.

**Deferred, dev-tooling only (never shipped to production users — the Docker frontend image
serves pre-built static files via nginx; no `vite`/`vitest`/`esbuild` process runs in it):**

| Package | Installed | Advisory | Why deferred |
|---|---|---|---|
| `vite` | 5.4.21 | GHSA-4w7w-66w2-5vf9 (High, path traversal in dev-server `.map` handling) + 2 more | Fix requires `vite@8.x` (major); dev-server-only exposure |
| `vitest` | 2.1.9 | GHSA-5xrq-8626-4rwp (Critical, arbitrary file read/exec via Vitest UI server) | Fix requires `vitest@4.x` (major); only reachable if the Vitest UI server (`vitest --ui`) is deliberately run and exposed, which this project's `package.json` scripts never do |
| `@vitest/mocker`, `vite-node`, `esbuild` | — | transitive to the above | Resolved by the same major bumps |

**Recommendation**: schedule the `vite@8`/`vitest@4` and `react-router@7` upgrades as their
own dedicated feature branches with full regression runs, given both are breaking-change
major versions. Do this before treating dependency hygiene as "done," not as an emergency —
none of the remaining findings are reachable in this app's actual deployed attack surface.

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
2. **No rate limiting on `/api/auth/login` or `/api/auth/register`.** There's nothing here to
   slow down a credential-stuffing or account-enumeration-via-registration attempt beyond the
   generic-error-message mitigation already in place (see above). Fine for local/personal use
   behind a trusted network; add `slowapi` or a reverse-proxy rate limit (e.g. nginx
   `limit_req`) on these two routes specifically before any public exposure.
3. **No email verification or password reset flow.** Registration accepts any syntactically
   valid email with no confirmation step, and there's no way to recover a lost password short
   of direct database access. Acceptable for a personal/local tool; a real deployment would
   need both before onboarding real users who might lose access.
4. **SQLite + no encryption at rest.** Judged acceptable for a single-user-per-account local
   deployment storing no PAN/bank data; add SQLCipher or filesystem-level encryption if the
   host disk isn't trusted. `hashed_password` is bcrypt-hashed regardless, so this specifically
   affects coupon/notification data, not credentials.
5. **General rate limiting**: no per-IP rate limiting on the FastAPI app as a whole beyond the
   auth-specific concern above. Fine for personal local use; add `slowapi` or a reverse-proxy
   rate limit before any public exposure.

## Summary

No Critical/Block findings reachable in this app's actual deployment. The two most severe
raw CVSS scores found (starlette 7.5, vite 8-ish for path traversal) are both dev-tooling-only
or verified-unreachable-in-this-codebase; documented with reasoning rather than asserted from
the CVSS number alone. Two dependency upgrades (FastAPI+Starlette, react-router v7) are
flagged as real, prioritized follow-up work — not silently ignored — because they require
dedicated breaking-change migrations this pass didn't have the scope to safely rush.

Real authentication now protects every personal-data endpoint (verified live with two
separate accounts and no data leakage between them); the two residual auth-related gaps
(no rate limiting on login/register, no email verification/password reset) are appropriate
for the app's current personal/local-use scope and are called out above, not silently
carried forward.
