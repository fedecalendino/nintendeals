import ddt
from unittest import TestCase

from nintendeals.api import prices


@ddt.ddt
class TestPrices(TestCase):

    @ddt.data(
        ("70010000000025", "US", "USD", 59.99),
        ("70010000000025", "CA", "CAD", 79.99),
        ("70010000000023", "AU", "AUD", 89.95),
        ("70010000000023", "CZ", "CZK", 1749.00),
        ("70010000000023", "ES", "EUR", 69.99),
        ("70010000000023", "GB", "GBP", 59.99),
        ("70010000000026", "JP", "JPY", 7678.00),
    )
    @ddt.unpack
    def test_get_price(self, nsuid, country, currency, value):
        price = prices.get_price(country, nsuid)

        self.assertEqual(nsuid, price.nsuid)
        self.assertEqual(country, price.country)
        self.assertEqual(currency, price.currency)
        self.assertEqual(value, price.value)
