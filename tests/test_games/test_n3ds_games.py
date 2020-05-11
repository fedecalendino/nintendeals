from nintendeals import noa, noe, noj
from nintendeals.classes import N3dsGame

from unittest import TestCase


class TestSwitchGames(TestCase):

    def test_noa(self):
        game: N3dsGame = noa.game_info(nsuid="50010000040656")

        self.assertEqual("Rhythm Heaven Megamix", str(game))

        self.assertEqual("50010000040656", game.nsuid)
        self.assertEqual("BPJ", game.unique_id)

        self.assertEqual("Nintendo", game.developer)
        self.assertEqual("Nintendo", game.publisher)

        self.assertEqual("NA", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2016, game.release_date.year)
        self.assertEqual(6, game.release_date.month)
        self.assertEqual(15, game.release_date.day)

        self.assertEqual(2, len(game.genres))
        self.assertEqual(4, game.players)

        self.assertEqual(
            "https://www.nintendo.com/en_US/games/detail/rhythm-heaven-megamix-3ds/",
            game.url(country="US")
        )

        self.assertEqual(
            "https://www.nintendo.com/fr_CA/games/detail/rhythm-heaven-megamix-3ds/",
            game.url(country="CA", lang="fr")
        )

        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertTrue(game.street_pass)
        self.assertFalse(game.virtual_console)

    def test_noe(self):
        game: N3dsGame = noe.game_info(nsuid="50010000041437")

        self.assertEqual("Rhythm Paradise Megamix", str(game))

        self.assertEqual("50010000041437", game.nsuid)
        self.assertEqual("BPJ", game.unique_id)

        self.assertIsNone(game.developer)
        self.assertEqual("Nintendo", game.publisher)

        self.assertEqual("EU", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2016, game.release_date.year)
        self.assertEqual(10, game.release_date.month)
        self.assertEqual(21, game.release_date.day)

        self.assertEqual(1, len(game.genres))
        self.assertEqual(4, game.players)

        self.assertEqual(
            "https://www.nintendo.co.uk/en/Games/Nintendo-3DS/Rhythm-Paradise-Megamix-1091313.html",
            game.url(country="GB")
        )

        self.assertEqual(
            "https://www.nintendo.co.za/en/Games/Nintendo-3DS/Rhythm-Paradise-Megamix-1091313.html",
            game.url(country="ZA")
        )

        self.assertEqual(
            "https://www.nintendo.it/it/Games/Nintendo-3DS/Rhythm-Paradise-Megamix-1091313.html",
            game.url(country="IT", lang="it")
        )

        self.assertTrue(game.demo)
        self.assertFalse(game.dlc)
        self.assertTrue(game.street_pass)
        self.assertFalse(game.virtual_console)

    def test_noj(self):
        game: N3dsGame = noj.game_info(nsuid="50010000033275")

        self.assertEqual("リズム天国 ザ･ベスト+", str(game))

        self.assertEqual("50010000033275", game.nsuid)
        self.assertEqual("BPJ", game.unique_id)

        self.assertEqual("任天堂", game.developer)
        self.assertIsNone(game.publisher)

        self.assertEqual("JP", game.region)
        self.assertEqual("Nintendo 3DS", game.platform)

        self.assertEqual(2015, game.release_date.year)
        self.assertEqual(6, game.release_date.month)
        self.assertEqual(11, game.release_date.day)

        self.assertEqual(2, len(game.genres))
        self.assertEqual(1, game.players)

        self.assertEqual(
            "https://www.nintendo.co.jp/titles/50010000033275",
            game.url(country="JP")
        )

        self.assertEqual(
            "https://www.nintendo.co.jp/titles/50010000033275",
            game.url(country="JP", lang="ja")
        )

        self.assertIsNone(game.demo)
        self.assertIsNone(game.dlc)
        self.assertIsNone(game.street_pass)
        self.assertFalse(game.virtual_console)

