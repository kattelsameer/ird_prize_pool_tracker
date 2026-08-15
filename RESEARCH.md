# Research Findings — Nepal IRD Taxpayer Incentive Gift Program (Prize Pool)

> Produced per CLAUDE.md §9. This is the authoritative research deliverable consulted before
> and during implementation. Findings marked **[LIVE]** were confirmed against the actual
> government API on 2026-08-15; findings marked **[SPEC]** come from the CLAUDE.md
> specification where live confirmation wasn't possible (e.g. the marketing site is a
> client-rendered SPA with no server-rendered body content, so program copy could not be
> scraped — the API is the reliable source instead).

## A. Domain Understanding

The Nepal Inland Revenue Department (IRD), under the Ministry of Finance, runs a
"Taxpayer Incentive Gift Program" (करदाता प्रोत्साहन उपहार कार्यक्रम). Consumers who obtain a
formal bill/invoice (or transact digitally through supported payment rails) are entered into
a coupon draw. IRD periodically draws winning coupon numbers and publishes them at
`prize.ird.gov.np`. The program exists to incentivize consumers to demand invoices, which
increases formal-economy visibility and tax compliance. **[SPEC]**

This application is an **independent, unofficial consumer tracker**. It reads IRD's public
data and compares it to coupons the user enters; it does not submit claims, does not talk to
IRD on the user's behalf, and does not imply government endorsement.

## B. Data Model — What IRD Actually Publishes **[LIVE]**

Confirmed request: `GET https://prize.ird.gov.np/api/v1/public/winners?limit=6&offset=0`
(no auth/cookie required for this public endpoint — it returned real data with only an
`Accept` and `User-Agent` header; the session cookies in the CLAUDE.md curl example are
incidental browser telemetry, not required credentials).

Confirmed live response shape:

```json
{
  "limit": 6,
  "offset": 0,
  "total_draws": 2,
  "has_more": false,
  "fiscal_years": [
    { "fiscal_year_code": "2083-84", "display_name": "FY 2083/84", "winner_count": 16 },
    { "fiscal_year_code": "2082-83", "display_name": "FY 2082/83", "winner_count": 0 }
  ],
  "categories": [
    { "category_id": "category_11e8...", "title_en": "Bumper Prize", "title_ne": "बम्पर पुरस्कार" },
    { "category_id": "category_31dc...", "title_en": "Daily Prize", "title_ne": "दैनिक पुरस्कार" }
  ],
  "draws": [
    {
      "draw_id": "draw_3dcfe8001afc31a805736567ea3ea74f",
      "category_title_en": "Bumper Prize",
      "category_title_ne": "बम्पर पुरस्कार",
      "draw_type": "GENERAL",
      "title_en": "Bumper Winner Consumer Selection for the period of Shrawan 1 to 15",
      "title_ne": "श्रावण १ गते देखी १५ गतेसम्मको बम्पर विजेता उपभोक्ता छनौट",
      "eligible_from": "2026-07-17",
      "eligible_to": "2026-07-31",
      "published_at": "2026-08-07T09:27:46.293223+05:45",
      "claim_deadline": "2026-08-22T09:27:46.293223+05:45",
      "claim_open": true,
      "winners": [
        { "winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493" }
      ]
    }
  ]
}
```

Key observations that differ from what a naive reading of the CLAUDE.md spec might suggest:

1. **Coupon numbers are a clean 12-digit numeric string** (`"007315254493"`), no spaces, no
   suffixes. The `"007 315 254 493BUMPER"` example in CLAUDE.md §10c appears to be a
   human-formatted display example, not the raw API value. Our normalizer still strips
   whitespace/non-digits defensively in case other draws or future API versions format
   differently.
2. `winner_rank` is a **plain integer** (1..15 for daily, 1 for bumper), not a string like
   `"BUMPER"`. Bumper vs. daily is distinguished by `category_title_en` / `draw_type` at the
   **draw** level, not by a rank string.
3. Timestamps (`published_at`, `claim_deadline`) are ISO-8601 **with an explicit `+05:45`
   offset** (Nepal Standard Time) already applied by the server — we do not need to guess the
   offset, but we still normalize everything through `Asia/Kathmandu` rather than trusting
   the offset blindly (defensive; the spec explicitly warns against naive tz assumptions).
4. `eligible_from` / `eligible_to` are **Gregorian calendar dates** (`"2026-07-17"`), not BS
   dates. BS fiscal year association is carried separately per-winner as
   `prize_fiscal_year_code` (e.g. `"2083-84"`), so the backend does not need to derive fiscal
   year from the Gregorian eligible-period dates — IRD already publishes it. We still
   implement Gregorian→BS conversion for **user-entered coupon transaction dates**, since
   users only know the Gregorian date of their purchase.
5. `claim_deadline = published_at + 15 days`, confirmed exactly (09:27:46 Aug 7 → 09:27:46
   Aug 22), matching the spec's 15-calendar-day claim window.
6. Pagination is `limit`/`offset` with a `has_more` boolean — matches spec.
7. No `network`/provider field is present in the winner record on this endpoint. This
   confirms §10e's guidance: network must be optional and must never gate a match.
8. `draw_type: "GENERAL"` is the only value observed so far (small sample); the field is
   preserved and passed through, but no special handling is implemented for other draw types
   since none have been observed — this is documented as a limitation.

## C. Matching Rules **[SPEC + inference from live shape]**

A user coupon **matches** a government record when:

1. `normalize(coupon_code) == normalize(prize_coupon_number)` (uppercase-fold, strip
   whitespace/hyphens; both sides already numeric-only in observed live data, so this is
   mostly a defensive no-op today).
2. The coupon's `fiscal_year` equals the winner's `prize_fiscal_year_code` **when the user
   has supplied a fiscal year**. If the fiscal year is unknown/blank, we still match on
   coupon code alone and flag the match as "fiscal year unconfirmed" rather than silently
   rejecting it (per §10e: prefer surfacing over hiding a possible win).
3. Network is **never** a rejection criterion (§10e, confirmed no network field exists in
   live payload anyway).
4. Multiple matches for one coupon (same code appearing in >1 draw) are all surfaced; this
   is logged as a data anomaly but not deduplicated away.

Transaction-date-vs-eligible-period validation is advisory only, not a matching gate: IRD's
`prize_coupon_number` is the authoritative signal that a specific transaction won. We surface
a warning if a user's entered transaction date falls outside every published eligible period
for the matching fiscal year, since that indicates likely user data-entry error, but we do
not use it to suppress a coupon-code match.

## D/E. Date & Fiscal-Year Logic

- All backend datetime handling is timezone-aware, converted to `Asia/Kathmandu` before any
  business-logic comparison (claim countdowns, sync scheduling, "is this within 2 days"
  checks).
- BS↔AD conversion uses the `nepali_datetime` Python package (pure-Python port of the
  standard Nepali calendar reference tables, MIT licensed) for converting a user's Gregorian
  transaction date into a BS date/fiscal-year label for display and for the advisory
  eligible-period check in (C) above. IRD's own fiscal-year label on winner records is used
  as-is and is authoritative — we never recompute or override it.
- Fiscal year boundary: BS Shrawan 1 ≈ Gregorian July 16/17 (varies slightly year to year
  because BS months are not fixed-length); we rely on the calendar library's real conversion
  table rather than a hardcoded "July 17" constant, and unit-test the 2026-07-16/2026-07-17
  boundary explicitly using the actual live-observed period boundaries above.

## F. Claim Logic

`claim_deadline` is published directly by IRD per draw (confirmed = `published_at` + 15
days). We use IRD's value verbatim rather than recomputing it, per §66/§68 (government value
is authoritative; recompute only as a cross-check, never as an override). Claim status
derived by the app:

- `CLAIM_ACTIVE` — now < claim_deadline and claim_open is true
- `CLAIM_EXPIRING` — claim_deadline - now < 2 days (dashboard/notification trigger, §33)
- `CLAIM_EXPIRED` — now >= claim_deadline or claim_open is false

## G. Network Logic

No network field observed on the public winners endpoint. The Coupon model still has an
optional `network` field for the user's own record-keeping (useful context for the user,
e.g. "I paid via eSewa"), but it is never used by the matching engine to accept/reject a
match, per §10e and confirmed absence in live data.

## H. API Behavior Summary

- Endpoint: `GET /api/v1/public/winners?limit=&offset=`, JSON, no auth required for reads.
- Pagination via `limit`/`offset` + `has_more`; no documented max `limit` observed — we cap
  our own client request size defensively (100) and page through with backoff.
- No documented rate limit headers observed; we self-limit (see Sync Service) to avoid
  hammering a small government service (§39).
- Errors: not observed live (no 4xx/5xx triggered during research); client code still
  handles timeout, connection error, non-200 status, and JSON-decode failure explicitly,
  since government uptime is not guaranteed (§39/§68).

## I. Risks

- **Site inaccessible for HTML research**: `prize.ird.gov.np`'s root page is a client-rendered
  SPA shell with no server-rendered body text, so program marketing copy (full T&Cs, exact
  prize amounts, exact draw-schedule prose) could not be scraped directly. We rely on
  CLAUDE.md §10a for that narrative content and label it as spec-sourced, not IRD-confirmed,
  on the in-app Information page.
- **Small live sample (2 draws, 16 winners)**: some structural assumptions (e.g. `draw_type`
  only ever being `"GENERAL"`, no `network` field ever appearing) are based on a small
  sample and could change as IRD's program matures. The adapter layer isolates this risk.
- **No documented API versioning/changelog**: schema drift is possible without notice; the
  adapter/normalization layer (§67) is the mitigation.
- **Coupon code collisions across fiscal years**: not observed but structurally possible;
  matching logic keys on (coupon_code, fiscal_year) pair, not coupon_code alone, to avoid
  false cross-year matches while still surfacing fiscal-year-unconfirmed matches (see C.2).

## J. Product Improvements Beyond the Spec

- An explicit "data confidence" badge on the Information page distinguishing "confirmed from
  live IRD API" vs "described in program materials" content, given finding I above.
- A manual "Re-check now" sync button surfaced next to the dashboard's sync status, in
  addition to the daily automatic sync, since users who just entered a coupon right after a
  draw was announced will want to check immediately.
- Duplicate-coupon-entry guard in the UI (warn, don't block, since manual+digital dual
  pathways can legitimately produce near-duplicate entries per §10a).
