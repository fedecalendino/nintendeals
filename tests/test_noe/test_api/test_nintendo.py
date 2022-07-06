from unittest import TestCase

import ddt

from nintendeals.commons.enumerates import Platforms
from nintendeals.noe.api import nintendo

LIMIT = 20


@ddt.ddt
class TestNintendo(TestCase):
    @ddt.data(
        (Platforms.NINTENDO_SWITCH, "700", "HAC"),
    )
    @ddt.unpack
    def test_search_by_platform(self, platform, nsuid_prefix, playable_on):
        result = nintendo.search_by_platform(platform)

        for index, data in enumerate(result):
            if index > LIMIT:
                break

            nsuid = data.get("nsuid_txt", "")
            playable_ons = data.get("playable_on_txt", [])

            if nsuid:
                self.assertTrue(nsuid.startswith(nsuid_prefix))

            if playable_ons:
                self.assertIn(playable_on, " ".join(playable_ons))
