from datetime import datetime
from unittest import TestCase

import ddt

from nintendeals import noa, noe, noj
from nintendeals.constants import SWITCH, NA, EU, JP


@ddt.ddt
class TestSearchSwitchGames(TestCase):

    @ddt.data(
        (noa, NA),
        (noe, EU),
        (noj, JP),
    )
    @ddt.unpack
    def test_search_switch_games(self, nintendo, region):
        game = next(nintendo.search_switch_games(
            title="Hollow Knight",
            released_after=datetime(2018, 6, 11),
            released_before=datetime(2018, 6, 13),
        ))

        self.assertIn("Hollow Knight", game.title)
        self.assertEqual(region, game.region)
        self.assertEqual(SWITCH, game.platform)
        self.assertFalse(game.free_to_play)

        if game.unique_id:
            self.assertEqual("AKLH", game.unique_id)

        if game.developer:
            self.assertEqual("Team Cherry", game.developer)

        if game.players:
            self.assertEqual(1, game.players)

