# Project Context (MTG Middle Class Checker)

## Current Status
- Flask web app is implemented and running locally.
- Primary branch: `main`
- Secondary branch kept in sync: `feature/web-rare-finder`
- Remote: `origin` -> `https://github.com/mjpolifka/mtg-middle-class-checker.git`

## Implemented Features
- Analyze a single Archidekt deck by deck ID.
- Analyze all decks in a public Archidekt folder by folder ID.
- Folder mode runs per-deck analysis concurrently and renders each deck's results.
- Rare/mythic filtering excludes configured ignored sets.
- `TLE` was added to ignored sets.

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
  - `pipenv run python -m flask --app app run --port 5001 --no-reload`
- App URL:
  - `http://127.0.0.1:5001`

## Recent Milestone Commits
- `48d0ce8` Build initial Flask web app
- `b31e1a8` Fix Scrython result handling + lockfile refresh
- `d57da5c` Ignore `TLE` set
- `3116d44` Add folder mode + concurrent multi-deck analysis
- `e67640b` Global Scryfall throttle to 5 rps

## Notes
- `demo.py` was intentionally left unchanged per user request.
- Default working port is `5001` to avoid conflict with local app on `4173`.
