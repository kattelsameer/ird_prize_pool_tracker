# Security Review Notes

Reviewed per CLAUDE.md §47 / §10d and the principal-security-engineer skill's checklist
(secure code review + secrets/infra posture lenses; the Guardsix-specific threat-modeling
procedure in that skill targets Guardsix's own on-prem product line and doesn't apply to this
greenfield project, so the generic checklist was used instead).

## What was checked

- **No secrets committed.** `.env.example` files document required env vars with no real
  values; `.gitignore` excludes `.env`, `data/*.db`, `node_modules/`, `__pycache__/`,
  `dist/`, `.venv/`.
- **No PII/PAN/bank data model.** `ConsumerProfile`/`Coupon` intentionally have no
  citizenship/PAN/bank fields — those only matter at in-person claim time and are out of
  this app's data model entirely, per §10d's "do not transmit PAN/bank details" rule taken
  to its logical conclusion (don't even collect them).
- **CORS** is env-driven (`CORS_ORIGINS`), not wildcarded to `*` with credentials in the
  default config.
- **Error handling**: a global FastAPI exception handler returns a generic message and logs
  full detail server-side only (`app/main.py`) — no stack traces or internals reach the
  client.
- **Input validation**: all API inputs go through Pydantic schemas; list endpoints bound
  `limit`/`offset` (e.g. `limit: int = Query(default=50, ge=1, le=200)`) to prevent
  unbounded queries.
- **SQL injection**: all data access goes through SQLAlchemy ORM query construction
  (`repositories/*.py`); no raw string-interpolated SQL was found anywhere in the codebase.
- **Outbound HTTP (IRD client)**: fixed base URL from config, explicit timeout, capped
  retries with backoff, capped max pages (`max_pages=200`) — no unbounded loop, no SSRF
  vector (URL is not user-influenced).
- **Logging**: `app/core/logging.py` configures structured logs of operational events only;
  no coupon codes, transaction dates, or profile data are logged (spot-checked
  `sync_service.py` / `matching_service.py` log calls — they log counts/IDs, not raw PII).
- **Docker**: backend image installs only pinned `requirements.txt` deps; no `--privileged`,
  no host network mode; nginx frontend image serves static files only, proxies `/api/` to
  the backend service by Docker Compose service name (not a user-controllable value).

## Residual risks / accepted limitations (documented, not silently ignored)

1. **No authentication.** Per §23, this is intentionally a local/single-profile app for now
   (`get_or_create_default_profile` always resolves to one implicit profile). This is
   acceptable for a personal-use consumer tool run by one person against their own Docker
   Compose stack, but **must not** be exposed on a shared/public network as-is. If this is
   ever deployed multi-tenant or publicly reachable, add real authentication before that
   happens — the data model (`profile_id` foreign keys already exist throughout) supports
   adding it without a schema rewrite.
2. **SQLite + no encryption at rest.** §10d recommends "encrypted local storage if needed."
   For a single-user local deployment storing no PAN/bank data, this was judged acceptable;
   if deployed where the host disk isn't trusted, add SQLCipher or filesystem-level
   encryption.
3. **Rate limiting**: no per-IP rate limiting on the FastAPI app itself (only the outbound
   IRD client self-limits). Fine for single-user local use; add `slowapi` or a reverse-proxy
   rate limit before any public exposure.
4. **Dependency review**: pinned versions are declared in `backend/requirements.txt` and
   `frontend/package.json`, but this sandbox could not reach PyPI/npm to run `pip-audit` /
   `npm audit` (see README "Known Environment Limitation"). Run those before production use.

No Block/Major findings. These are documented Minor/accepted-risk items appropriate for the
stated scope (a personal consumer tracker), not defects.
