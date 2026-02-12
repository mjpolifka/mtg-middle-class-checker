import unittest
from unittest.mock import MagicMock, patch

import app


class FetchAllPrintingsTests(unittest.TestCase):
    @patch("app.throttle_scryfall")
    @patch("app.requests.get")
    def test_fetch_all_printings_follows_next_page(self, mock_get, _mock_throttle):
        first = MagicMock()
        first.raise_for_status.return_value = None
        first.json.return_value = {
            "data": [{"name": "Sol Ring", "set": "lea"}],
            "has_more": True,
            "next_page": "https://api.scryfall.com/cards/search?page=2",
        }

        second = MagicMock()
        second.raise_for_status.return_value = None
        second.json.return_value = {
            "data": [{"name": "Sol Ring", "set": "2ed"}],
            "has_more": False,
        }

        mock_get.side_effect = [first, second]

        results = app._fetch_all_printings("Sol Ring")

        self.assertEqual(2, len(results))
        self.assertEqual("lea", results[0]["set"])
        self.assertEqual("2ed", results[1]["set"])
        self.assertEqual(2, mock_get.call_count)


class FolderDeckParsingTests(unittest.TestCase):
    @patch("app.requests.get")
    def test_get_folder_decks_parses_next_data_when_script_attrs_reordered(self, mock_get):
        payload = (
            '{"props":{"pageProps":{"redux":{"folders":{"rootFolder":{"decks":'
            '[{"id":1,"name":"Deck One"},{"id":2,"name":"Deck Two"}]}}}}}}'
        )
        html = (
            "<html><head></head><body>"
            f'<script type="application/json" id="__NEXT_DATA__">{payload}</script>'
            "</body></html>"
        )

        response = MagicMock()
        response.raise_for_status.return_value = None
        response.text = html
        mock_get.return_value = response

        decks = app.get_folder_decks(1209082)

        self.assertEqual([(1, "Deck One"), (2, "Deck Two")], decks)


class IndexUnifiedIdInputTests(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    @patch("app.find_rare_printings")
    def test_deck_mode_uses_archidekt_id(self, mock_find_rare_printings):
        mock_find_rare_printings.return_value = ("Deck Name", {})

        response = self.client.post(
            "/",
            data={"mode": "deck", "archidekt_id": "123"},
        )

        self.assertEqual(200, response.status_code)
        mock_find_rare_printings.assert_called_once_with(123)

    @patch("app.analyze_folder")
    def test_folder_mode_uses_archidekt_id(self, mock_analyze_folder):
        mock_analyze_folder.return_value = ("Folder 123", [])

        response = self.client.post(
            "/",
            data={"mode": "folder", "archidekt_id": "123"},
        )

        self.assertEqual(200, response.status_code)
        mock_analyze_folder.assert_called_once_with(123)

    def test_unified_id_requires_numeric_input(self):
        response = self.client.post(
            "/",
            data={"mode": "deck", "archidekt_id": "not-a-number"},
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"ID must be numeric.", response.data)


class IgnoreSetListTests(unittest.TestCase):
    def test_mountain_rare_promo_sets_are_ignored(self):
        expected = {
            "G17",
            "P23",
            "PAL00",
            "PAL01",
            "PAL03",
            "PAL99",
            "PARL",
            "PGPX",
            "PGRU",
            "PMPS06",
            "PPP1",
            "PSS2",
            "PSS3",
            "PSS4",
        }
        self.assertTrue(expected.issubset(app.IGNORED_SETS))


if __name__ == "__main__":
    unittest.main()
