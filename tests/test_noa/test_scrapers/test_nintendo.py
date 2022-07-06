from unittest import TestCase

import ddt

from nintendeals.noa.scrapers import nintendo


@ddt.ddt
class TestNintendo(TestCase):
    @ddt.data(
        (
            "the-legend-of-zelda-breath-of-the-wild-switch",
            "70010000000025",
            "HACPAAAAA",
            "The Legend of Zelda™: Breath of the Wild",
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
        self.assertEqual(product_code, result["product_code"])
        self.assertEqual(slug, result["slug"])
        self.assertEqual(title, result["title"])
