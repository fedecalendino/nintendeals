from unittest import TestCase

from nintendeals import noa
from nintendeals.commons.enumerates import Features, Ratings, Regions, Platforms


class TestGameInfo(TestCase):
    def test_game_info_non_existant(self):
        game = noa.game_info(nsuid="60010000000000")
        self.assertIsNone(game)

        game = noa.game_info(slug="unknown")
        self.assertIsNone(game)

        game = noa.game_info()
        self.assertIsNone(game)

    def test_game_info_switch(self):
        game = noa.game_info(slug="super-smash-bros-ultimate-switch")

        self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
        self.assertEqual(game.region, Regions.NA)
        self.assertEqual(game.title, "Super Smash Bros.™ Ultimate")
        self.assertEqual(game.nsuid, "70010000012332")
        self.assertEqual(game.unique_id, "AAAB")

        self.assertEqual(game.slug, "super-smash-bros-ultimate-switch")

        self.assertEqual(game.players, 8)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.ESRB, "Everyone 10+"))

        self.assertEqual(game.release_date.year, 2018)
        self.assertEqual(game.release_date.month, 12)
        self.assertEqual(game.release_date.day, 7)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.DEMO), False)
        self.assertEqual(game.features.get(Features.DLC), True)
        self.assertEqual(game.features.get(Features.NSO_REQUIRED), True)
        self.assertEqual(game.features.get(Features.SAVE_DATA_CLOUD), True)

        self.assertEqual(
            game.eshop.ca_fr,
            "https://www.nintendo.com/fr_CA/games/detail/super-smash-bros-ultimate-switch",
        )
