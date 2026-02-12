import time
import json
import re
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import scrython
from flask import Flask, render_template, request
from pyrchidekt.api import getDeckById
import requests

app = Flask(__name__)


IGNORED_SETS = {
    # Unusual Sets
    "SLD",  # Secret Lairs
    "SLP",  # Secret Lair Showdown
    "SLC",  # Secret Lair 30th Anniversary Countdown Kit
    "SPG",  # Special Guests
    "TLE",  # Through the Omenpaths
    "HOP",  # Planechase
    "PLST",  # The List
    # Promos and similar
    "PRM",
    "SCH",
    "F01",
    "F02",
    "F03",
    "F04",
    "F05",
    "F06",
    "F07",
    "F08",
    "F09",
    "F10",
    "F11",
    "F12",
    "F13",
    "F14",
    "F15",
    "JGP",
    "G00",
    "G01",
    "G02",
    "G03",
    "G04",
    "G05",
    "G06",
    "G07",
    "G08",
    "G09",
    "G10",
    "G11",
    "J12",
    "J13",
    "J14",
    "J15",
    "J16",
    "J17",
    "J18",
    "J22",
    "J23",
    "J24",
    "J25",
    "P08",
    "P09",
    "P10",
    "P22",
    "PZ1",
    "PZ2",
    "PIDW",
    "PURL",
    "PMEI",
    "PKLD",
    "PDGM",
    "PDTK",
    "PANA",
    "PHPR",
    "P30M",
    "P30A",
    "PSVC",
    "PFDN",
    "RFIN",
    "PF19",
    "PF20",
    "PF21",
    "PF22",
    "PF23",
    "PF24",
    "PF25",
    "PLGM",
    "DCI",
    "PJAS",
    "PJJT",
    "PJSE",
    "PSUS",
    "PUMA",
    "PEWK",
    "PCBB",
    "PL23",
    "PL24",
    "PL25",
    "PW21",
    "PW22",
    "PW23",
    "PW24",
    "PW25",
    "PLG20",
    "PLG21",
    "PLG22",
    "PLG23",
    "PLG24",
    "PAL04",
    "PAL05",
    "PAL06",
    # Signature spellbook / FTV / commander collection
    "SS1",
    "SS2",
    "SS3",
    "V09",
    "V12",
    "V13",
    "DRB",
    "CC1",
    "CC2",
    # Bonus sheets
    "STA",
    "BRR",
    "MUL",
    "WOT",
    "OTP",
    "BIG",
    "H2R",
    "FCA",
    "EOS",
    "MAR",
    "OMB",
    # Masterpiece series
    "EXP",
    "MPS",
    "MP2",
    "ZNE",
    "MED",
    # MTGO masters
    "ME1",
    "ME2",
    "ME3",
    "ME4",
    "VMA",
    "TPR",
    # Physical masters
    "MMA",
    "MM2",
    "MM3",
    "EMA",
    "IMA",
    "A25",
    "UMA",
    "CMM",
    "2XM",
    "2X2",
    # Remasters
    "TSR",
    "DMR",
    "RVR",
    "INR",
    "DBL",
    # Arena remasters
    "AKR",
    "KLR",
    "SIR",
    "SIS",
    "PIO",
    # Commander precons
    "C20",
    "ZNC",
    "KHC",
    "C21",
    "AFC",
    "MIC",
    "VOC",
    "NEC",
    "NCC",
    "DMC",
    "BRC",
    "ONC",
    "MOC",
    "LTC",
    "WOC",
    "LCC",
    "MKC",
    "OTC",
    "M3C",
    "BLC",
    "DSC",
    "DRC",
    "TDC",
    "SCD",
    "CMA",
}


@dataclass
class RarePrinting:
    set_name: str
    set_code: str
    collector_number: str
    rarity: str


@dataclass
class DeckAnalysis:
    deck_id: int
    deck_name: str
    rare_results: dict[str, list[RarePrinting]]
    error: str | None = None


def _printing_as_dict(printing: object) -> dict:
    if isinstance(printing, dict):
        return printing
    if hasattr(printing, "to_dict") and callable(printing.to_dict):
        return printing.to_dict()
    return {
        "name": getattr(printing, "name", ""),
        "set": getattr(printing, "set", ""),
        "set_name": getattr(printing, "set_name", ""),
        "collector_number": getattr(printing, "collector_number", ""),
        "rarity": getattr(printing, "rarity", ""),
    }


def find_rare_printings(deck_id: int) -> tuple[str, dict[str, list[RarePrinting]]]:
    deck = getDeckById(deck_id)
    rare_by_card: dict[str, list[RarePrinting]] = {}
    seen_names = set()

    for card in deck.cards:
        card_name = card.card.oracle_card.name
        if card_name in seen_names:
            continue
        seen_names.add(card_name)

        query = scrython.cards.Search(unique="prints", q=card_name)
        rares: list[RarePrinting] = []
        results = query.data() if callable(query.data) else query.data
        for raw_printing in results:
            printing = _printing_as_dict(raw_printing)
            if printing["name"] != card_name:
                continue
            if printing["rarity"] in {"common", "uncommon"}:
                continue
            if printing["set"].upper() in IGNORED_SETS:
                continue
            rares.append(
                RarePrinting(
                    set_name=printing["set_name"],
                    set_code=printing["set"].upper(),
                    collector_number=printing["collector_number"],
                    rarity=printing["rarity"],
                )
            )
        if rares:
            rare_by_card[card_name] = rares
        time.sleep(0.1)  # be polite to Scryfall

    return deck.name, dict(sorted(rare_by_card.items()))


def get_folder_decks(folder_id: int) -> list[tuple[int, str]]:
    response = requests.get(f"https://archidekt.com/folders/{folder_id}", timeout=20)
    response.raise_for_status()
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(?P<json>.*?)</script>',
        response.text,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("Unable to parse folder data from Archidekt page.")

    payload = json.loads(match.group("json"))
    decks = (
        payload.get("props", {})
        .get("pageProps", {})
        .get("redux", {})
        .get("folders", {})
        .get("rootFolder", {})
        .get("decks", [])
    )
    if not decks:
        return []

    return [(deck["id"], deck["name"]) for deck in decks if "id" in deck and "name" in deck]


def analyze_folder(folder_id: int) -> tuple[str, list[DeckAnalysis]]:
    decks = get_folder_decks(folder_id)
    if not decks:
        return f"Folder {folder_id}", []

    results: list[DeckAnalysis] = []
    workers = min(4, len(decks))

    def run_deck(deck_id: int, fallback_name: str) -> DeckAnalysis:
        try:
            deck_name, rares = find_rare_printings(deck_id)
            return DeckAnalysis(deck_id=deck_id, deck_name=deck_name, rare_results=rares)
        except Exception as exc:
            return DeckAnalysis(
                deck_id=deck_id,
                deck_name=fallback_name,
                rare_results={},
                error=str(exc),
            )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(run_deck, deck_id, deck_name): (deck_id, deck_name)
            for deck_id, deck_name in decks
        }
        for future in as_completed(future_map):
            results.append(future.result())

    # Keep output deterministic by deck name.
    results.sort(key=lambda deck_result: deck_result.deck_name.lower())
    return f"Folder {folder_id}", results


@app.route("/", methods=["GET", "POST"])
def index():
    deck_name = None
    deck_id = ""
    folder_id = ""
    mode = "deck"
    rare_results = None
    folder_results = None
    folder_title = None
    error = None

    if request.method == "POST":
        mode = request.form.get("mode", "deck").strip()
        if mode == "folder":
            folder_id = request.form.get("folder_id", "").strip()
            if not folder_id.isdigit():
                error = "Folder ID must be numeric."
            else:
                try:
                    folder_title, folder_results = analyze_folder(int(folder_id))
                except Exception as exc:
                    error = f"Unexpected error: {exc}"
        else:
            deck_id = request.form.get("deck_id", "").strip()
            if not deck_id.isdigit():
                error = "Deck ID must be numeric."
            else:
                try:
                    deck_name, rare_results = find_rare_printings(int(deck_id))
                except RuntimeError:
                    error = f"No deck found for ID {deck_id}."
                except Exception as exc:  # broad catch for network/api issues
                    error = f"Unexpected error: {exc}"

    return render_template(
        "index.html",
        mode=mode,
        deck_id=deck_id,
        folder_id=folder_id,
        deck_name=deck_name,
        rare_results=rare_results,
        folder_results=folder_results,
        folder_title=folder_title,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
