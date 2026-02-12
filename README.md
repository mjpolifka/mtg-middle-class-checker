# MTG Rare Printing Finder (Web App)

This project now includes a Flask web app version of the deck analyzer.

## Run locally

1. Install dependencies:
   - `pipenv install`
2. Start the app:
   - `pipenv run python app.py`
3. Open:
   - `http://127.0.0.1:5000`

## Usage

1. Choose a search mode:
   - `By Deck ID`
   - `By Folder ID`
2. Enter the relevant Archidekt ID and submit.
3. Review cards with rare/mythic printings (excluding sets in the ignored list).
