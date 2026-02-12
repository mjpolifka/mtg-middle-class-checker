# Project Context (MTG Middle Class Checker)

## Current Status
- Flask web app is implemented and running locally.
- Primary branch: `main`
- Secondary branch kept in sync: `feature/web-rare-finder`
- Remote: `origin` -> `https://github.com/mjpolifka/mtg-middle-class-checker.git`
- Active feature branch for current work: `feat/single-id-ui-dev-script-mountain-ignore`

## Implemented Features
- Analyze a single Archidekt deck by deck ID.
- Analyze all decks in a public Archidekt folder by folder ID.
- Folder mode runs per-deck analysis concurrently and renders each deck's results.
- Rare/mythic filtering excludes configured ignored sets.
- `TLE` was added to ignored sets.
- UI now uses one `Archidekt ID` input; mode dropdown decides deck vs folder lookup.
- Added `run_dev_server.ps1` as the standard local dev server launch command.
- Added unit tests with `unittest` for pagination, folder parsing, unified ID mode behavior, and ignore-list guards.
- Added additional ignored promo/basic-land sets so `Mountain` rare promo printings do not appear.

## Reliability / API Handling
- Fixed Scrython compatibility issues:
  - `Search.data` may be property or callable.
  - Search items may be dict-like or object-like.
- Added global Scryfall throttle:
  - Scryfall documented max: 10 requests/sec
  - App target: 5 requests/sec (half of documented max)
  - Implemented as a shared lock + monotonic interval limiter.

## Local Run
- Start:
  - `pipenv install`
  - `.\run_dev_server.ps1`
- App URL:
  - `http://127.0.0.1:5001`
- Tests:
  - `pipenv run python -m unittest discover -s tests -v`

## Recent Milestone Commits
- `48d0ce8` Build initial Flask web app
- `b31e1a8` Fix Scrython result handling + lockfile refresh
- `d57da5c` Ignore `TLE` set
- `3116d44` Add folder mode + concurrent multi-deck analysis
- `e67640b` Global Scryfall throttle to 5 rps

## Notes
- `demo.py` was intentionally left unchanged per user request.
- Default working port is `5001` to avoid conflict with local app on `4173`.
- `main` branch merges require explicit user QA approval before proceeding.
- At the start of each new session, run the base command `git` so prefix approvals can cover all follow-up git commands.
- Branch policy: use one feature branch per feature. Do not combine multiple features in one branch.

## Open Roadmap (Keep Reminding User Until Built)
- Move Scryfall API workload to the client/user side (or equivalent architecture) so requests are not centralized on server rate limits.
- Stream partial analysis results to the UI while processing (likely incremental updates via JS/AJAX or similar).
- Add progress bars per deck so users can track remaining work/time during analysis.
- Apply the same basic-land rare-printing suppression approach used for `Mountain` to `Island`, `Plains`, `Forest`, and `Swamp`.

## Next Planned Feature
- After the current pause/review cycle, run another review before merging to `main`.

## Main Merge Workflow (Standard)
- For any merge into `main`, perform a thorough pre-merge review (tests, change inspection, and risk review), then update `CONTEXT.md` with the review outcome and workflow reminders so they are included in the merge.

## Pre-Main Review (2026-02-12)
- Scope reviewed: `app.py`, `templates/index.html`, `tests/test_app.py`, `run_dev_server.ps1`, `README.md`, and this context file.
- Validation run:
  - `pipenv run python -m unittest discover -s tests -v` (all tests passing)
  - `python -m py_compile app.py tests\test_app.py` (pass)
- Outcome:
  - No blocking defects found for current changes.
  - Residual risk: folder extraction currently searches for the first `decks` list in parsed payload; if Archidekt page payload shape changes significantly, it may still need adjustment.
  - Merge status: candidate is technically ready pending explicit user QA approval for `main`.
