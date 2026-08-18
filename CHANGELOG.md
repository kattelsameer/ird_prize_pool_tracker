# Changelog

All notable changes to this project are documented here, grouped by release.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [SemVer](https://semver.org/) per `CLAUDE.md` §18a.

All `0.x.y` releases are pre-1.0: the app is functional and tested, but the
data model and API may still change before a stable `1.0.0`.

## [Unreleased]

Nothing yet — changes accumulate here until the next release is cut.

## [0.2.0] - 2026-08-18

### Added

- Draw-period status per coupon: shows which fortnightly IRD draw window a
  coupon's transaction date falls into, whether that draw has actually been
  published yet (using real synced data) or is only estimated from the BS
  calendar cadence, and flags gaps where sync coverage is missing.

### Fixed

- Registration no longer auto-logs the user in; it redirects to the login
  page with a "account created" confirmation instead.
- `.gitignore`'s unanchored `lib/` rule was silently excluding
  `frontend/src/lib/` from version control since the project's first commit.

### Docs

- Added `known_issues.md` to track unrelated bugs found in passing instead of
  fixing them inline.

## [0.1.0] - Initial release

Core features available to consumers at this beta launch:

- Multi-user accounts with email/password login and per-user profiles.
- Coupon management: add, edit, delete, search, and filter your coupons.
- Automatic daily sync with the IRD prize-pool system, with sync status
  visible in-app.
- Matching engine that checks your coupons against published prize-pool
  results, with claim-status tracking (active / expiring / expired).
- Dashboard highlighting winning coupons, notices, and recent updates.
- Prize-pool explorer for browsing and filtering published draw results.
- Notifications for new matches, approaching claim deadlines, and sync
  issues.
- Settings for managing networks and notification preferences.
- Personal data export and deletion.
- Responsive, mobile-friendly UI.
- Full Docker Compose setup for running the whole stack locally.
