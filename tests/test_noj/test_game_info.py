from unittest import TestCase

from nintendeals import noj
from nintendeals.commons.enumerates import Features, Ratings, Regions, Platforms


class TestGameInfo(TestCase):
    def test_game_info_non_existant(self):
        game = noj.game_info("60010000000000")
        self.assertIsNone(game)

    def test_game_info_switch(self):
        game = noj.game_info("70010000012085")

        self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
        self.assertEqual(game.region, Regions.JP)
        self.assertEqual(game.title, "大乱闘スマッシュブラザーズ SPECIAL")
        self.assertEqual(game.nsuid, "70010000012085")
        self.assertEqual(game.unique_id, "AAAB")

        self.assertEqual(game.players, 8)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.CERO, "A"))

        self.assertEqual(game.release_date.year, 2018)
        self.assertEqual(game.release_date.month, 12)
        self.assertEqual(game.release_date.day, 7)

        self.assertIn("任天堂", game.developers)

        self.assertEqual(game.features.get(Features.AMIIBO), True)
        self.assertEqual(game.features.get(Features.DLC), True)
        self.assertEqual(game.features.get(Features.NSO_REQUIRED), True)

        self.assertEqual(
            game.eshop.jp_jp,
            "https://store-jp.nintendo.com/list/software/70010000012085.html",
        )
