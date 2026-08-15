# Sajha Coupon Tracker

*(Nepali "साझा" — "shared/common" — a consumer-friendly name for the "Nepal IRD Prize Pool
Consumer Tracker" suggested in the project spec. See "Naming" below.)*

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

## Naming

Chosen after research (CLAUDE.md §10): memorable, consumer-friendly, descriptive, and
explicitly avoids implying government ownership/endorsement. Feel free to rename freely —
the name appears only in `README.md`, `package.json`, and the FastAPI `title` in
`backend/app/main.py`.

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

Frontend and backend are separate Docker images/containers on purpose (CLAUDE.md §20), so the
backend can later be reused by a mobile client without touching the API contract.

Government data, user data, and application-derived data (matches/claim-status/notifications)
are stored and displayed as distinct categories throughout — see `DataSourceBadge` in the
frontend and the raw-vs-normalized storage split in `PrizePoolWinner` (CLAUDE.md §6/§10d/§66).

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
| `VITE_API_BASE_URL` | frontend | base path/URL the SPA calls; `/api` behind the nginx proxy in Docker |

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

# Frontend E2E (Playwright, against a mocked backend fixture — never live IRD)
cd frontend && npx playwright install --with-deps && npm run e2e
```

Backend tests follow a strict `test_x.py` + `data_x.py` pairing (scenario tables live in the
`data_*.py` file, never as literals inside test bodies) and mock the IRD HTTP layer via
`httpx.MockTransport` — no test ever touches the live network. See `backend/tests/`.

## Synchronization & matching logic (summary — see `RESEARCH.md` for the full findings)

- Daily sync at `00:00 Asia/Kathmandu` (APScheduler `CronTrigger(timezone="Asia/Kathmandu")`),
  plus a manual `POST /api/sync` trigger.
- A coupon matches when its normalized code equals a published `prize_coupon_number`. Fiscal
  year is checked when the user supplied one, but a mismatch is surfaced as
  "fiscal year unconfirmed," never silently hidden. Network is never a matching criterion
  (IRD's live API doesn't even publish one).
- Claim status (`CLAIM_ACTIVE` / `CLAIM_EXPIRING` / `CLAIM_EXPIRED`) is computed from IRD's
  own `claim_deadline`/`claim_open` fields in `Asia/Kathmandu` — the app never invents its
  own deadline.
- A failed sync never deletes or overwrites existing data; it's recorded in `SyncRun` and
  surfaced in the UI ("Government data could not be updated. Existing data is still
  available.").

## Git workflow

`master` (stable) ← `develop` (integration) ← `feature/*` / `bugfix/*`, per CLAUDE.md §11-18.
Run `git log --oneline --all --decorate --graph` to see the full branch/merge history —
initial feature build-out (`feature/project-scaffold`, `feature/backend-foundation`,
`feature/matching-engine`, `feature/frontend-app`, `feature/docker-and-release`), plus
several rounds of bugfix branches found by actually running the Dockerized app (timezone/test
fixtures, a SQLite/TestClient connection-pool isolation bug, a validation-error serialization
crash, a missing "newly eligible coupon" notification, and a systemic frontend/backend API
contract drift across pagination, notifications, matches, and settings — each merged through
`develop` before reaching `master`).

## Known limitations / assumptions

This project was originally built in a sandbox with no package-registry or Docker access, so
an earlier revision of this section described what *couldn't* be verified there. It has since
been fully built, tested, and Dockerized end-to-end in a real environment — the numbers below
are actual, current results, not estimates:

- **Backend**: 55 pytest tests pass (`cd backend && pytest`), covering models, repositories,
  every API route (including live-verified sort/filter/pagination on `/api/prize-pools` and
  add/rename/deactivate on `/api/settings/networks`), matching rules, claim-status boundaries,
  the Nepal fiscal-year boundary, normalization, sync idempotency/failure-handling, and the
  IRD client's retry/backoff/pagination logic against a mocked transport.
- **Frontend**: 43 Vitest/RTL tests pass (`cd frontend && npm test`), `tsc --noEmit` is clean,
  the production build (`npm run build`) succeeds, and the Playwright E2E spec
  (`npm run e2e`) passes the full consumer journey against a deterministic mock backend.
- **Docker**: `docker compose up --build` builds and starts both containers; both pass their
  health checks; a real sync against the live `prize.ird.gov.np` API, coupon CRUD, matching,
  notifications, claim countdowns, and settings/network management were all manually verified
  against the running containers in a browser, including that data (coupons, synced winners)
  survives a container restart.
- **`nepali_datetime` (BS↔AD conversion)** is installed and active — confirmed via a direct
  check that `app/domain/nepali_calendar.py` takes the real-library path (not its anchor-table
  fallback) and that it agrees with CLAUDE.md's own worked example (July 16/17, 2026 falling
  on either side of the FY2082-83/2083-84 boundary). The fallback table remains in place for
  any environment where the package genuinely isn't installed; nothing in the matching engine
  depends on it being exact either way, since IRD publishes `prize_fiscal_year_code` directly.
- **Single implicit consumer profile, no authentication** — appropriate for local/personal
  use per CLAUDE.md §23; see `SECURITY.md` before any shared/public deployment.
- **IRD site body content could not be scraped** (client-rendered SPA, no server HTML) — the
  live API was fetched directly instead and is the authoritative source used throughout;
  see `RESEARCH.md` for exactly what was confirmed live vs. sourced from the spec.
- At the time of this build, live sync returned 1 draw period / 16 winner records (15 daily +
  1 bumper) — some structural assumptions (e.g., no `network` field, `draw_type` always
  `"GENERAL"`) rest on a small sample; the adapter layer (`app/schemas/prize_pool.py`'s
  `PrizePoolWinnerRead.from_model`) isolates this risk if the API's shape evolves.
- **Dependency security**: two dependency advisories (a FastAPI/Starlette CVE set, and a
  react-router open-redirect CVE) are fixed only in major-version upgrades and are deferred
  as prioritized follow-up work rather than fixed blind under time pressure — see
  `SECURITY.md` for the full reachability analysis (neither is actually exploitable in this
  app's current code) and exact upgrade path.

## Project layout

```
backend/    FastAPI app, SQLAlchemy models/migrations, IRD integration, matching/sync/
            notification services, pytest suite, Dockerfile
frontend/   React + TS + Vite SPA, component/E2E tests, Dockerfile + nginx
RESEARCH.md Domain research findings (CLAUDE.md §9 deliverable)
SECURITY.md Security review notes and accepted-risk log
```
