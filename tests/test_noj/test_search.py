from unittest import TestCase

from nintendeals import noj
from nintendeals.commons.enumerates import Platforms, Regions

LIMIT = 20


class TestListing(TestCase):
    def test_list_3ds_games(self):
        index = 0

        for index, game in enumerate(noj.search_3ds_games("ゼルダ")):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_3DS)
            self.assertEqual(game.region, Regions.JP)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("500"))

        self.assertNotEqual(index, 0)

    def test_list_switch_games(self):
        index = 0

        for index, game in enumerate(noj.search_switch_games("ゼルダ")):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
            self.assertEqual(game.region, Regions.JP)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("700"))

        self.assertNotEqual(index, 0)

    def test_list_wiiu_games(self):
        index = 0

        for index, game in enumerate(noj.search_wiiu_games("ゼルダ")):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_WIIU)
            self.assertEqual(game.region, Regions.JP)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("200"))

        self.assertNotEqual(index, 0)
