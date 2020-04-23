from unittest import TestCase

import ddt

from nintendeals import noa, noe, noj
from nintendeals.constants import SWITCH, NA, EU, JP


@ddt.ddt
class TestDetails(TestCase):

    LIMIT = 200

    @ddt.data(
        (noa, NA),
        (noe, EU),
        (noj, JP),
    )
    @ddt.unpack
    def test_listings(self, nintendo, region):
        count = 0

        for game in nintendo.list_games(SWITCH):
            if count == self.LIMIT:
                break

            count += 1

            self.assertIsNotNone(game.title)
            self.assertEqual(region, game.region)
            self.assertEqual(SWITCH, game.platform)

