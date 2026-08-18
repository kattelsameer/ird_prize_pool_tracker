# Known Issues

Bugs and inconsistencies noticed in passing while working on something else. Tracked here
instead of fixed inline so unrelated work doesn't get bundled into an unrelated change.

## Resolved

- **`.gitignore`'s unanchored `lib/` rule swallowed `frontend/src/lib/`.** The Python-template
  rule `lib/` (meant for a stray venv `lib` folder) has no leading slash, so it matched a
  directory named `lib` at any depth, including `frontend/src/lib/`. That silently excluded
  `claimStatus.ts`, `coupon.ts`, `fiscalYears.ts`, and their tests from every commit in this
  project's history -- only this working tree having the files on disk made the build/tests
  appear to pass. A fresh clone would have been missing them entirely.
  Fixed in `bugfix/gitignore-swallows-frontend-lib` (anchored to `/lib/`, `/lib64/`; added the
  previously-untracked files to version control), merged to `develop`/`master`.
