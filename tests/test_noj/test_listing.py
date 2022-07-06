from unittest import TestCase

from nintendeals import noj
from nintendeals.commons.enumerates import Platforms, Regions

LIMIT = 20


class TestListing(TestCase):
    def test_list_switch_games(self):
        for index, game in enumerate(noj.list_switch_games()):
            if index > LIMIT:
                break

            self.assertEqual(game.platform, Platforms.NINTENDO_SWITCH)
            self.assertEqual(game.region, Regions.JP)

            if game.nsuid:
                self.assertTrue(game.nsuid.startswith("700"))
