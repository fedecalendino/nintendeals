from unittest import TestCase

from nintendeals.api import prices


class TestPrices(TestCase):

    def test_fetch_prices(self):
        data = {
            "70010000000025": 59.99,  # Breath of the Wild (Switch)
            "70010000020033": 59.99,  # Link's Awakening (Switch)
        }

        fetched_prices = prices.fetch_prices(country="US", nsuids=list(data))

        for nsuid, price in fetched_prices:
            self.assertIn(price.nsuid, data)

            expected_price = data[price.nsuid]

            self.assertEqual("US", price.country)
            self.assertEqual("USD", price.currency)
            self.assertEqual(expected_price, price.value)

    def test_non_existent_prices(self):
        data = [
            "50010000000000",
            "60010000000000",
            "70010000000000"
        ]

        fetched_prices = prices.fetch_prices(country="US", nsuids=data)

        for nsuid, price in fetched_prices:
            self.assertIn(nsuid, data)
            self.assertIsNone(price)

    def test_fetch_prices_nsuid_limit(self):
        data = [f"700100000000{i}" for i in range(100)]

        with self.assertRaises(ValueError) as context:
            fetched_prices = prices.fetch_prices(country="US", nsuids=data)

            for nsuid, price in fetched_prices:
                print(nsuid, price)

        self.assertEqual(
            "The amount of nsuids must between 1 and 50.",
            str(context.exception)
        )
