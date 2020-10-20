from unittest import TestCase

import ddt

from nintendeals.noj.api import nintendo

LIMIT = 100


@ddt.ddt
class TestNintendo(TestCase):

    # @ddt.data(
    #     (Platforms.NINTENDO_WII_U, "2001", ["WUP"]),
    #     (Platforms.NINTENDO_3DS, "5001", ["CTR", "KTR"]),
    #     (Platforms.NINTENDO_SWITCH, "7001", ["HAC"]),
    # )
    # @ddt.unpack
    # def test_software(self, platform, nsuid_prefix, playable_on):
    #     for index, data in enumerate(nintendo.software(platform)):
    #         if index > LIMIT:
    #             print(data)
    #             break
    #
    #         self.assertIn(nsuid_prefix, data["LinkURL"])
    #         self.assertIn(data["InitialCode"][:3], playable_on)

    @ddt.data(
        ("20010000019347", "BD3J", "WUP"),
        ("50010000042737", "AWHJ", "CTR"),
        ("70010000032983", "AY6QA", "HAC"),
    )
    @ddt.unpack
    def test_search(self, nsuid, icode, hard):
        data = nintendo.search(nsuid)

        self.assertEqual(icode, data["icode"])
        self.assertIn(hard, data["hard"])

    def test_search_unknown(self):
        data = nintendo.search("1123581321")
        self.assertIsNone(data)
