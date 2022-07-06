from unittest import TestCase

import ddt

from nintendeals.noa.scrapers import nintendo


@ddt.ddt
class TestNintendo(TestCase):
    @ddt.data(
        (
            "the-legend-of-zelda-the-wind-waker-hd-wii-u",
            "20010000001646",
            "WUPPBCZE",
            "The Legend of Zelda: The Wind Waker HD",
        ),
        (
            "the-legend-of-zelda-ocarina-of-time-3d-3ds",
            "50010000000541",
            "CTRPAQEE",
            "The Legend of Zelda: Ocarina of Time 3D",
        ),
        (
            "the-legend-of-zelda-links-awakening-switch",
            "70010000020033",
            "HACPAR3NA",
            "The Legend of Zelda™: Link’s Awakening",
        ),
    )
    @ddt.unpack
    def test_search_by_nsuid(self, slug, nsuid, product_code, title):
        result = nintendo.scrap(slug)

        self.assertEqual(nsuid, result["nsuid"])
        # self.assertEqual(product_code, result["product_code"])  TODO
        self.assertEqual(slug, result["slug"])
        self.assertEqual(title, result["title"])
