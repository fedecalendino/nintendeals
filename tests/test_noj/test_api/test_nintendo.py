from unittest import TestCase

import ddt

from nintendeals.commons.enumerates import Platforms
from nintendeals.noj.api import nintendo

LIMIT = 100


@ddt.ddt
class TestNintendo(TestCase):
    @ddt.data(
        (Platforms.NINTENDO_SWITCH, "700", "1_HAC"),
    )
    @ddt.unpack
    def test_search_by_platform(self, platform, nsuid_prefix, hard):
        result = nintendo.search_by_platform(platform)

        for index, data in enumerate(result):
            if index > LIMIT:
                break

            self.assertEqual(hard, data["hard"])

            nsuid = data["nsuid"]

            if nsuid:
                self.assertEqual(nsuid_prefix, nsuid[:3])

    @ddt.data(
        ("70010000000026", "AAAAA", "1_HAC"),
        ("70010000032983", "AY6QA", "1_HAC"),
    )
    @ddt.unpack
    def test_search_by_nsuid(self, nsuid, icode, hard):
        data = nintendo.search_by_nsuid(nsuid)

        self.assertEqual(icode, data["icode"])
        self.assertEqual(hard, data["hard"])

    def test_search_by_unknown_nsuid(self):
        data = nintendo.search_by_nsuid("1123581321")
        self.assertIsNone(data)
