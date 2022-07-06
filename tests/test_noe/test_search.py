from unittest import TestCase

from nintendeals import noe
from nintendeals.commons.enumerates import Platforms, Regions

LIMIT = 20


class TestListing(TestCase):
    def test_list_switch_games(self):
        index = 0

        for index, game in enumerate(noe.search_switch_games("Zelda")):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
            self.assertEqual(game.region, Regions.EU)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("700"))

        self.assertNotEqual(index, 0)
