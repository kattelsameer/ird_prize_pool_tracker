# Security Policy

## Reporting a vulnerability

Please report security issues privately via
[GitHub Security Advisories](../../security/advisories/new) rather than opening a public
issue. Include steps to reproduce and, if possible, the potential impact. We'll acknowledge
reports as quickly as we can and aim to have a fix released before any public disclosure.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |
| < 0.1.0 | ❌ |

Security fixes are applied to `master` and released under a new patch version. Always run the
latest tagged release.

## Security measures

- **Authentication**: passwords are hashed with bcrypt and never logged or stored in
  plaintext. Login/register return identical generic error messages regardless of which
  check failed, to resist account enumeration. JWTs fail closed on any validation problem
  (expired, malformed, wrong signature, unknown user) with a single 401.
- **Rate limiting**: `/api/auth/login` and `/api/auth/register` share a per-IP budget to slow
  down credential stuffing.
- **Data isolation**: every account has its own private profile; coupons, notifications, and
  settings are scoped per-account and never visible across accounts. Published prize-pool
  data is the one deliberately public, unauthenticated endpoint.
- **Data minimization**: the app never collects or stores PAN, citizenship, or bank details —
  those are only needed at in-person claim time and are entirely outside this app's data
  model.
- **Data rights**: accounts can export everything they've entered as JSON, or permanently
  delete their account and all associated data in one action.
- **Input validation**: all API input is validated through Pydantic schemas; list endpoints
  bound `limit`/`offset` to prevent unbounded queries.
- **Database access**: exclusively through the SQLAlchemy ORM — no raw string-interpolated
  SQL anywhere in the codebase.
- **Outbound requests** (the IRD client): fixed base URL from config, explicit timeout, capped
  retries with backoff, capped max pages — no unbounded loops, no user-influenced URLs.
- **Error handling**: a global exception handler returns a generic message to clients and logs
  full detail server-side only; no stack traces or internals are ever returned in a response.
- **CORS** is configured via an explicit allow-list (`CORS_ORIGINS`), never wildcarded with
  credentials enabled.
- **Dependencies** are checked with `pip-audit` (backend) and `npm audit` (frontend); both
  currently report zero known vulnerabilities.

## Known limitations

- **`JWT_SECRET` must be changed before any shared or public deployment.** The built-in
  default exists only so `docker compose up` works out of the box for local/demo use; startup
  logs a warning if it's still in use. Set a real random value via the `JWT_SECRET`
  environment variable first.
- **No email verification or password reset flow.** Registration accepts any syntactically
  valid email with no confirmation step, and a lost password currently has no self-service
  recovery path. Acceptable for a personal/local tool; a public deployment onboarding real
  users would need both.
- **SQLite with no encryption at rest.** Reasonable for a single-user-per-account local
  deployment that stores no PAN/bank data; add SQLCipher or filesystem-level encryption if the
  host disk isn't trusted. Passwords are bcrypt-hashed regardless, so this affects
  coupon/notification data, not credentials.
- **Rate limiting is scoped to the auth endpoints only.** Add a reverse-proxy rate limit
  (e.g. nginx `limit_req`) in front of the whole API before any public exposure.
