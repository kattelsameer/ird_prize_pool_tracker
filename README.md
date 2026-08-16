# Sajha Coupon Tracker

*(Nepali "साझा" — "shared/common")*

An independent, unofficial web application that helps consumers in Nepal track their
purchase coupons against prize-pool results published by the Inland Revenue Department (IRD)
under the Taxpayer Incentive Gift Program (करदाता प्रोत्साहन उपहार कार्यक्रम).

**This project is not affiliated with, endorsed by, or operated by the Government of Nepal
or the IRD.** It reads IRD's public data (`prize.ird.gov.np`) and compares it to coupons you
enter yourself; it never submits anything to IRD on your behalf, and a "match" only ever
means *"this coupon code appears in IRD's published winner list,"* never *"you are
guaranteed a prize."* Claiming a prize still requires your original physical bill, a valid
PAN, a government photo ID, and an in-person visit to an Inland Revenue Office within IRD's
15-day claim window — see the in-app **Information** page for the full process.

## Features

- Track your own purchase coupons (add/edit/delete/search/filter) alongside their fiscal
  year, transaction date, and payment network.
- Daily sync against IRD's public winners API, with matching against your coupons.
- A dashboard that surfaces what actually needs your attention: new matches, claim
  deadlines, and sync failures — not just charts.
- Claim-status tracking (`active` / `expiring soon` / `expired`) computed from IRD's own
  published claim deadlines.
- A prize-pool explorer with server-side search, filtering, sorting, and pagination.
- Personal data controls: export everything you've entered as JSON, or permanently delete
  your account.

## Architecture

```
React + TS (Vite) ──HTTP/JSON──▶ FastAPI ──▶ SQLAlchemy ──▶ SQLite
      (frontend/)                 (backend/app/api)         (backend/data/app.db)
                                        │
                    ┌───────────────────┼────────────────────┐
                    ▼                   ▼                    ▼
            Matching Service    Notification Service    Sync Service (APScheduler,
            (app/services)      (app/services)          Asia/Kathmandu, daily 00:00)
                                                                │
                                                                ▼
                                                      IRD Client + Adapter
                                                (app/integrations/ird — the ONLY
                                                 module that knows IRD's HTTP shape)
```

Frontend and backend run as separate Docker images/containers, so the backend can later be
reused by a mobile client without touching the API contract.

Government data, user data, and application-derived data (matches, claim status,
notifications) are stored and displayed as distinct categories throughout — see
`DataSourceBadge` in the frontend and the raw-vs-normalized storage split in
`PrizePoolWinner`.

## Prerequisites

- Docker + Docker Compose (recommended path), **or**
- Python 3.11+ and Node.js 20+ for local (non-Docker) development

## Quick start (Docker)

```bash
cp .env.example .env        # optional: set DEMO_MODE=true to try the UI with seeded fixtures
docker compose up --build
```

- Frontend: http://localhost:8080
- Backend API + docs: http://localhost:8000/docs
- The backend container runs `alembic upgrade head` automatically on every start
  (`backend/Dockerfile`'s `CMD`), before starting uvicorn; `Base.metadata.create_all`
  (`app/main.py`) is a secondary safety net for a completely fresh SQLite file.

## Local development (without Docker)

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
DEMO_MODE=true uvicorn app.main:app --reload --port 8000   # DEMO_MODE seeds fixtures + skips live sync

# Frontend (separate terminal)
cd frontend
npm install
npm run dev   # http://localhost:5173, proxies /api to http://localhost:8000 in dev via VITE_API_BASE_URL
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full list. Key ones:

| Var | Where | Meaning |
|---|---|---|
| `DATABASE_URL` | backend | SQLAlchemy URL, defaults to a local SQLite file |
| `DEMO_MODE` | backend | `true` = seed deterministic demo fixtures, skip live IRD sync/scheduler |
| `CORS_ORIGINS` | backend | comma-separated allowed frontend origins |
| `IRD_API_BASE_URL` | backend | defaults to the real `https://prize.ird.gov.np/api/v1/public` |
| `JWT_SECRET` | backend | signs login tokens; **the built-in default is insecure and logs a startup warning** — set a real random value (`python3 -c "import secrets; print(secrets.token_hex(32))"`) before any shared/public deployment |
| `VITE_API_BASE_URL` | frontend | base path/URL the SPA calls; `/api` behind the nginx proxy in Docker |

## Authentication

Real accounts: `POST /api/auth/register` (email + password, min 8 characters) and
`POST /api/auth/login` both return a JWT the frontend stores in `localStorage` and sends as
`Authorization: Bearer <token>` on every request (`src/api/client.ts`). Both endpoints share a
per-IP rate limit (10 requests/minute — `app/core/rate_limit.py`) to slow down credential
stuffing. Each account gets its own private profile — coupons, notifications, and settings are
all scoped to it and never visible to another account. `GET /api/prize-pools` (published
government data) is the one deliberate exception and stays public/unauthenticated.

In `DEMO_MODE=true`, a seeded demo account is created automatically — check the backend
container logs for `Demo mode: seeded deterministic demo fixtures. Log in with <email> / <password>`
(credentials aren't hardcoded here so they don't drift from `scripts/seed_demo.py`).

**Your data** (Settings → Account): view/edit your display name, download a JSON export of
everything you've entered (`GET /api/profile/export`), or permanently delete your account and
everything tied to it (`DELETE /api/profile`).

## Migrations

```bash
cd backend
alembic upgrade head       # apply
alembic revision --autogenerate -m "description"   # generate a new migration after model changes
```

## Testing

```bash
# Backend
cd backend && pip install -r requirements.txt && pytest

# Frontend unit/component tests
cd frontend && npm install && npm test

# Frontend lint + typecheck (run before any PR)
cd frontend && npm run lint && npm run typecheck

# Frontend E2E (Playwright, against a mocked backend fixture — never live IRD)
cd frontend && npx playwright install --with-deps && npm run e2e
```

Backend tests follow a `test_x.py` + `data_x.py` pairing (scenario tables live in the
`data_*.py` file, not as literals inside test bodies) and mock the IRD HTTP layer via
`httpx.MockTransport` — no test ever touches the live network. See `backend/tests/`.

## Synchronization & matching logic (summary — see `RESEARCH.md` for the full findings)

- Daily sync at `00:00 Asia/Kathmandu` (APScheduler `CronTrigger(timezone="Asia/Kathmandu")`),
  plus a manual `POST /api/sync` trigger.
- A coupon matches when its normalized code equals a published `prize_coupon_number`. Fiscal
  year is checked when the user supplied one, but a mismatch is surfaced as
  "fiscal year unconfirmed," never silently hidden. Network is never a matching criterion
  (IRD's live API doesn't publish one).
- Claim status (`active` / `expiring soon` / `expired`) is computed from IRD's own
  `claim_deadline`/`claim_open` fields in `Asia/Kathmandu` — the app never invents its own
  deadline.
- A failed sync never deletes or overwrites existing data; it's recorded and surfaced in the
  UI ("Government data could not be updated. Existing data is still available."). A failure
  also schedules a background retry at 1 hour, then 4 hours, then 24 hours — never
  immediately, and canceled automatically as soon as a sync succeeds again.

## Git workflow

`master` (stable) ← `develop` (integration) ← `feature/*` / `bugfix/*`. Feature and bugfix
branches are tested individually, merged into `develop`, integration-tested together, and
only then merged into `master`. Run `git log --oneline --all --decorate --graph` to see the
full branch/merge history.

## Known limitations / assumptions

- **Backend**: 92 pytest tests, covering models, repositories, every API route (including
  sort/filter/pagination on `/api/prize-pools`, network management, auth + per-account data
  isolation + rate limiting, and personal-data export/deletion), matching rules, claim-status
  boundaries, the Nepal fiscal-year boundary, normalization, password hashing/JWT roundtrip
  and expiry, sync idempotency/failure-handling and retry backoff, and the IRD client's
  retry/backoff/pagination logic against a mocked transport.
- **Frontend**: 59 Vitest/RTL tests, `tsc --noEmit` clean, `npm run lint` (ESLint) clean,
  production build succeeds, and both Playwright E2E specs pass — the full consumer journey,
  and register/logout/login — against a deterministic mock backend.
- **Dependencies**: `pip-audit`/`npm audit` both report 0 known vulnerabilities.
- **Docker**: `docker compose up --build` builds and starts both containers; both pass health
  checks; sync against the live `prize.ird.gov.np` API, coupon CRUD, matching, notifications,
  claim countdowns, and settings/network management have all been verified against the
  running containers, including that data survives a container restart.
- **BS↔AD conversion** uses the `nepali_datetime` package where available, with a fallback
  anchor-table conversion for environments where it isn't installed. The matching engine
  doesn't depend on either being exact, since IRD publishes `prize_fiscal_year_code` directly.
- **Multi-user accounts** — email/password login (bcrypt + JWT), each account gets its own
  private profile (coupons/notifications/settings scoped per-profile, never visible across
  accounts). Prize-pool data (`/api/prize-pools`) stays public/unauthenticated, since it's
  published government data, not personal to any account. See `SECURITY.md` for the
  `JWT_SECRET` requirement before any shared/public deployment.
- **IRD's marketing site could not be scraped for body copy** (it's a client-rendered SPA with
  no server-rendered HTML) — the live API was used as the source of truth instead; see
  `RESEARCH.md` for what was confirmed live vs. sourced from public program materials.
- At the time of writing, live sync returned a small sample of draws/winners, so some
  structural assumptions (e.g. no `network` field, `draw_type` always `"GENERAL"`) rest on
  limited data; the adapter layer (`app/schemas/prize_pool.py`) isolates this risk if the
  API's shape evolves.

## Project layout

```
backend/    FastAPI app, SQLAlchemy models/migrations, IRD integration, matching/sync/
            notification services, pytest suite, Dockerfile
frontend/   React + TS + Vite SPA, component/E2E tests, Dockerfile + nginx
RESEARCH.md Domain research and data-model findings
SECURITY.md Security posture and known limitations
```

## Contributing

Issues and pull requests are welcome. Please run the full test/lint/typecheck suite (see
Testing above) before opening a PR, and follow the branching model described in Git workflow.

## License

MIT — see `LICENSE`.
