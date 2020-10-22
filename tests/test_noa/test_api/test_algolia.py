from unittest import TestCase

import ddt

from nintendeals.commons.enumerates import Platforms
from nintendeals.noa.api import algolia

LIMIT = 20


@ddt.ddt
class TestAlgolia(TestCase):

    @ddt.data(
        ("20010000001646", "the-legend-of-zelda-the-wind-waker-hd-wii-u"),
        ("50010000000541", "the-legend-of-zelda-ocarina-of-time-3d-3ds"),
        ("70010000020033", "the-legend-of-zelda-links-awakening-switch"),
    )
    @ddt.unpack
    def test_search_by_nsuid(self, nsuid, slug):
        result = algolia.search_by_nsuid(nsuid)
        self.assertEqual(slug, result["slug"])

    @ddt.data(
        (Platforms.NINTENDO_WIIU, "2001", "Wii U"),
        (Platforms.NINTENDO_3DS, "5001", "Nintendo 3DS"),
        (Platforms.NINTENDO_SWITCH, "7001", "Nintendo Switch"),
    )
    @ddt.unpack
    def test_search_by_query(self, platform, nsuid_prefix, playable_on):
        result = algolia.search_by_query(
            query="Zelda",
            platform=platform
        )

        for index, data in enumerate(result):
            if index > LIMIT:
                break

            self.assertIn("Zelda", data.get("title"))
            self.assertIn(playable_on, data.get("platform"))

            nsuid = data.get("nsuid")

            if nsuid:
                self.assertIn(nsuid_prefix, nsuid)

    @ddt.data(
        (Platforms.NINTENDO_WIIU, "2001", "Wii U"),
        (Platforms.NINTENDO_3DS, "5001", "Nintendo 3DS"),
        (Platforms.NINTENDO_SWITCH, "7001", "Nintendo Switch"),
    )
    @ddt.unpack
    def test_search_by_platform(self, platform, nsuid_prefix, playable_on):
        result = algolia.search_by_platform(platform)

        for index, data in enumerate(result):
            if index > LIMIT:
                break

            self.assertIn(nsuid_prefix, data.get("nsuid"))
            self.assertIn(playable_on, data.get("platform"))
