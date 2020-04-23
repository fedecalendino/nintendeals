from unittest import TestCase

import ddt

from nintendeals.classes.games import Game
from nintendeals.constants import SWITCH, NA, EU, JP


@ddt.ddt
class TestPrices(TestCase):

    @ddt.data(
        ("70010000000025", NA, "US", "USD", 59.99),
        ("70010000000025", NA, "CA", "CAD", 79.99),
        ("70010000000023", EU, "AU", "AUD", 89.95),
        ("70010000000023", EU, "CZ", "CZK", 1749.00),
        ("70010000000023", EU, "ES", "EUR", 69.99),
        ("70010000000023", EU, "GB", "GBP", 59.99),
        ("70010000000026", JP, "JP", "JPY", 7678.00),
    )
    @ddt.unpack
    def test_get_price(self, nsuid, region, country, currency, value):
        game = Game(
            title="title",
            region=region,
            platform=SWITCH,
            nsuid=nsuid,
        )

        price = game.price(country)

        self.assertEqual(nsuid, price.nsuid)
        self.assertEqual(country, price.country)
        self.assertEqual(currency, price.currency)
        self.assertEqual(value, price.value)

