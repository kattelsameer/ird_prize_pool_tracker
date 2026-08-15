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
- The backend runs `alembic upgrade head` is **not** auto-invoked by the container today —
  run it once against the mounted volume (see Migrations below) or rely on the
  `Base.metadata.create_all` startup safety-net (`app/main.py`) for a fresh SQLite file.

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
Run `git log --oneline --all --decorate --graph` to see the branch/merge history for this
build. Feature branches used for this initial build: `feature/project-scaffold`,
`feature/backend-foundation`, `feature/matching-engine`, `feature/frontend-app`,
`feature/docker-and-release`.

## Known limitations / assumptions

1. **This cloud build environment could not reach PyPI or the npm registry** (org network
   allowlist blocks package-registry egress from this sandbox; confirmed directly with
   `pip install fastapi` → "No matching distribution found," and equivalently for npm). It
   also has no running Docker daemon. **Practically: `pip install -r requirements.txt`,
   `npm install`, `pytest`/`npm test`/`playwright test`, and `docker compose up --build` must
   all be run in an environment with normal internet access** (your own machine, CI, etc.) —
   they were not fabricated as "passing" here. What *was* actually executed in this sandbox,
   using only already-preinstalled tooling (to avoid claiming untested code works):
   - Backend: 27 dependency-free unit tests (`python -m unittest`) covering matching rules,
     claim-status boundaries, the Nepal fiscal-year boundary, normalization, and the IRD
     client's retry/backoff/pagination logic against a mocked transport — all passing. Every
     `.py` file passes `py_compile`. The SQLAlchemy/FastAPI layer (models, API routes,
     sync service) is fully written and unit-tested in `backend/tests/`, but those specific
     tests need `pip install` to actually execute — do that before merging to `master` in a
     real CI run.
   - Frontend: `tsc --noEmit` against the real source with stub type declarations (clean);
     the pure business-logic modules (claim countdown math, coupon normalization) executed
     directly via `tsx` with 18/18 hand-written assertions passing. Vitest/RTL component
     tests and the Playwright E2E spec are fully written but need `npm install` to run.
2. **`nepali_datetime` (the BS↔AD conversion package named in the original plan) could not be
   verified installable here.** `backend/app/domain/nepali_calendar.py` tries importing it
   first and falls back to a small anchor-table implementation documented in that file,
   sufficient because IRD publishes `prize_fiscal_year_code` directly (the BS conversion is
   only used for advisory display/eligible-period checks, never for the matching decision
   itself). Verify/replace with the real package once you have registry access.
2. **Single implicit consumer profile, no authentication** — appropriate for local/personal
   use per CLAUDE.md §23; see `SECURITY.md` before any shared/public deployment.
3. **IRD site body content could not be scraped** (client-rendered SPA, no server HTML) — the
   live API was fetched directly instead and is the authoritative source used throughout;
   see `RESEARCH.md` for exactly what was confirmed live vs. sourced from the spec.
4. Only two live draws / 16 winner records existed at research time — some structural
   assumptions (e.g., no `network` field, `draw_type` always `"GENERAL"`) rest on a small
   sample; the adapter layer isolates this risk if the API's shape evolves.

## Project layout

```
backend/    FastAPI app, SQLAlchemy models/migrations, IRD integration, matching/sync/
            notification services, pytest suite, Dockerfile
frontend/   React + TS + Vite SPA, component/E2E tests, Dockerfile + nginx
RESEARCH.md Domain research findings (CLAUDE.md §9 deliverable)
SECURITY.md Security review notes and accepted-risk log
```
