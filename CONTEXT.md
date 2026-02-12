# Project Context (MTG Middle Class Checker)

## Current Status
- Flask web app is implemented and running locally.
- Primary branch: `main`
- Remote: `origin` -> `https://github.com/mjpolifka/mtg-middle-class-checker.git`
- Active feature branch for current work: `feat/single-id-ui-dev-script-mountain-ignore`

## Implemented Features
- Analyze a single Archidekt deck by deck ID.
- Analyze all decks in a public Archidekt folder by folder ID.
- Folder mode runs per-deck analysis concurrently and renders each deck's results.
- Rare/mythic filtering excludes configured ignored sets.
- UI now uses one `Archidekt ID` input; mode dropdown decides deck vs folder lookup.
- Added `run_dev_server.ps1` as the standard local dev server launch command.
- Added unit tests with `unittest` for pagination, folder parsing, unified ID mode behavior, and ignore-list guards.

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
- Find any sets where the following cards are printed as rare, and add those sets to the ignore list: `Island`, `Plains`, `Forest`, and `Swamp`.

## Main Merge Workflow (Standard)
- For any merge into `main`, first update `CONTEXT.md` with any new context up to this point, then perform a thorough pre-merge review (tests, change inspection, and risk review), then explain your review to the user and ask for confirmation before merging.
