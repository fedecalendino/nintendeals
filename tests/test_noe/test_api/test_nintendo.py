from unittest import TestCase

import ddt

from nintendeals.commons.enumerates import Platforms
from nintendeals.noe.api import nintendo

LIMIT = 20


@ddt.ddt
class TestNintendo(TestCase):

    @ddt.data(
        (Platforms.NINTENDO_WIIU, "2001", "WUP"),
        (Platforms.NINTENDO_3DS, "5001", "CTR"),
        (Platforms.NINTENDO_SWITCH, "7001", "HAC"),
    )
    @ddt.unpack
    def test_search_by_platform(self, platform, nsuid_prefix, playable_on):
        result = nintendo.search_by_platform(platform)

        for index, data in enumerate(result):
            if index > LIMIT:
                break

            nsuids = data.get("nsuid_txt", [])
            playable_ons = data.get("playable_on_txt", [])

            if nsuids:
                self.assertIn(nsuid_prefix, " ".join(nsuids))

            if playable_ons:
                self.assertIn(playable_on, " ".join(playable_ons))
