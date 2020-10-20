from unittest import TestCase

import ddt

from nintendeals.noe.api import nintendo
from nintendeals.commons.enumerates import Platforms


LIMIT = 20


@ddt.ddt
class TestNintendo(TestCase):

    @ddt.data(
        (Platforms.NINTENDO_WII_U, "2001", "WUP"),
        (Platforms.NINTENDO_3DS, "5001", "CTR"),
        (Platforms.NINTENDO_SWITCH, "7001", "HAC"),
    )
    @ddt.unpack
    def test_search(self, platform, nsuid_prefix, playable_on):
        for index, data in enumerate(nintendo.search(platform)):
            if index > LIMIT:
                break

            nsuids = data.get("nsuid_txt", [])
            playable_ons = data.get("playable_on_txt", [])

            if nsuids:
                self.assertIn(nsuid_prefix, " ".join(nsuids))

            if playable_ons:
                self.assertIn(playable_on, " ".join(playable_ons))
