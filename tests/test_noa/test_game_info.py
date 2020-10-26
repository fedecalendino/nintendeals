from unittest import TestCase

from nintendeals import noa
from nintendeals.commons.enumerates import Features, Ratings, Regions, Platforms


class TestGameInfo(TestCase):

    def test_game_info_non_existant(self):
        game = noa.game_info("60010000000000")
        self.assertIsNone(game)

    def test_game_info_3ds(self):
        game = noa.game_info("50010000023235")

        self.assertEqual(game.platform, Platforms.NINTENDO_3DS)
        self.assertEqual(game.region, Regions.NA)
        self.assertEqual(game.title, "Super Smash Bros.")
        self.assertEqual(game.nsuid, "50010000023235")
        self.assertEqual(game.unique_id, "AXC")

        self.assertEqual(game.slug, "super-smash-bros-for-nintendo-3ds")

        self.assertEqual(game.players, 4)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.ESRB, "Everyone 10+"))

        self.assertEqual(game.release_date.year, 2014)
        self.assertEqual(game.release_date.month, 10)
        self.assertEqual(game.release_date.day, 3)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.DEMO), True)

        self.assertEqual(game.eshop.ca_en, "https://www.nintendo.com/en_CA/games/detail/super-smash-bros-for-nintendo-3ds")

    def test_game_info_switch(self):
        game = noa.game_info("70010000012332")

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

        self.assertEqual(game.eshop.ca_fr, "https://www.nintendo.com/fr_CA/games/detail/super-smash-bros-ultimate-switch")

    def test_game_info_wiiu(self):
        game = noa.game_info("20010000007686")

        self.assertEqual(game.platform, Platforms.NINTENDO_WIIU)
        self.assertEqual(game.region, Regions.NA)
        self.assertEqual(game.title, "Super Smash Bros.")
        self.assertEqual(game.nsuid, "20010000007686")
        self.assertEqual(game.unique_id, "AXF")

        self.assertEqual(game.slug, "super-smash-bros-for-wii-u")

        self.assertEqual(game.players, 8)
        self.assertFalse(game.free_to_play)

        self.assertEqual(game.rating, (Ratings.ESRB, "Everyone 10+"))

        self.assertEqual(game.release_date.year, 2014)
        self.assertEqual(game.release_date.month, 11)
        self.assertEqual(game.release_date.day, 21)

        self.assertIn("Nintendo", game.publishers)

        self.assertEqual(game.features.get(Features.DEMO), False)

        self.assertEqual(game.eshop.us_en, "https://www.nintendo.com/en_US/games/detail/super-smash-bros-for-wii-u")
