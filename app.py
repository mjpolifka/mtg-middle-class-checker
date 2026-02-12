import time
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from html.parser import HTMLParser

from flask import Flask, render_template, request
from pyrchidekt.api import getDeckById
import requests

app = Flask(__name__)

SCRYFALL_DOCUMENTED_MAX_RPS = 10
SCRYFALL_TARGET_RPS = SCRYFALL_DOCUMENTED_MAX_RPS / 2
SCRYFALL_MIN_INTERVAL_SECONDS = 1.0 / SCRYFALL_TARGET_RPS
_scryfall_rate_lock = Lock()
_next_scryfall_request_time = 0.0


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
    # Promo basic land sets that can appear as rare
    "PARL",
    "PAL99",
    "PAL00",
    "PAL01",
    "PAL03",
    "G17",
    "P23",
    "PGPX",
    "PGRU",
    "PMPS06",
    "PPP1",
    "PSS2",
    "PSS3",
    "PSS4",
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


class _NextDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_next_data = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        attributes = dict(attrs)
        if attributes.get("id") == "__NEXT_DATA__":
            self._in_next_data = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_next_data:
            self._in_next_data = False

    def handle_data(self, data: str) -> None:
        if self._in_next_data:
            self._parts.append(data)

    @property
    def next_data(self) -> str:
        return "".join(self._parts).strip()


def throttle_scryfall() -> None:
    global _next_scryfall_request_time
    with _scryfall_rate_lock:
        now = time.monotonic()
        wait_seconds = _next_scryfall_request_time - now
        if wait_seconds > 0:
            time.sleep(wait_seconds)
            now = time.monotonic()
        _next_scryfall_request_time = max(now, _next_scryfall_request_time) + SCRYFALL_MIN_INTERVAL_SECONDS


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


def _fetch_all_printings(card_name: str) -> list[dict]:
    params = {"unique": "prints", "q": card_name}
    url = "https://api.scryfall.com/cards/search"
    results: list[dict] = []

    while url:
        throttle_scryfall()
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        page_results = payload.get("data", [])
        if isinstance(page_results, list):
            results.extend(page_results)
        url = payload.get("next_page") if payload.get("has_more") else None
        params = None

    return results


def _extract_next_data_payload(html: str) -> dict:
    parser = _NextDataParser()
    parser.feed(html)
    next_data = parser.next_data
    if not next_data:
        raise RuntimeError("Unable to parse folder data from Archidekt page.")
    return json.loads(next_data)


def _extract_decks_from_payload(payload: dict) -> list[dict]:
    def walk(node: object) -> list[dict]:
        if isinstance(node, dict):
            decks = node.get("decks")
            if isinstance(decks, list) and all(isinstance(deck, dict) for deck in decks):
                return decks
            for value in node.values():
                found = walk(value)
                if found:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = walk(value)
                if found:
                    return found
        return []

    return walk(payload)


def find_rare_printings(deck_id: int) -> tuple[str, dict[str, list[RarePrinting]]]:
    deck = getDeckById(deck_id)
    rare_by_card: dict[str, list[RarePrinting]] = {}
    seen_names = set()

    for card in deck.cards:
        card_name = card.card.oracle_card.name
        if card_name in seen_names:
            continue
        seen_names.add(card_name)

        rares: list[RarePrinting] = []
        results = _fetch_all_printings(card_name)
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

    return deck.name, dict(sorted(rare_by_card.items()))


def get_folder_decks(folder_id: int) -> list[tuple[int, str]]:
    response = requests.get(f"https://archidekt.com/folders/{folder_id}", timeout=20)
    response.raise_for_status()
    payload = _extract_next_data_payload(response.text)
    decks = _extract_decks_from_payload(payload)
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
    archidekt_id = ""
    mode = "deck"
    rare_results = None
    folder_results = None
    folder_title = None
    error = None

    if request.method == "POST":
        mode = request.form.get("mode", "deck").strip()
        archidekt_id = request.form.get("archidekt_id", "").strip()
        if not archidekt_id:
            legacy_field = "folder_id" if mode == "folder" else "deck_id"
            archidekt_id = request.form.get(legacy_field, "").strip()
        if not archidekt_id.isdigit():
            error = "ID must be numeric."
        elif mode == "folder":
            try:
                folder_title, folder_results = analyze_folder(int(archidekt_id))
            except Exception as exc:
                error = f"Unexpected error: {exc}"
        else:
            try:
                deck_name, rare_results = find_rare_printings(int(archidekt_id))
            except RuntimeError:
                error = f"No deck found for ID {archidekt_id}."
            except Exception as exc:  # broad catch for network/api issues
                error = f"Unexpected error: {exc}"

    return render_template(
        "index.html",
        mode=mode,
        archidekt_id=archidekt_id,
        deck_name=deck_name,
        rare_results=rare_results,
        folder_results=folder_results,
        folder_title=folder_title,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
