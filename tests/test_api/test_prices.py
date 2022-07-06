from unittest import mock, TestCase

import ddt

from nintendeals import noa
from nintendeals.api import prices

from tests.util import spy


@ddt.ddt
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
        data = ["50010000000000", "60010000000000", "70010000000000"]

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
            "The amount of nsuids must between 1 and 50.", str(context.exception)
        )

    def test_get_prices_chunks(self):
        nsuid = "70010000000025"
        game = noa.game_info(nsuid=nsuid)

        games = [game] * 222

        with spy(prices, "fetch_prices") as spied:
            found = list(prices.get_prices(games=games, country="US"))

        self.assertEqual(1, len(found))

        for nsuid, price in found:
            self.assertEqual(game.nsuid, nsuid)

            self.assertEqual("US", price.country)
            self.assertEqual("USD", price.currency)
            self.assertEqual(59.99, price.value)

        self.assertEqual(5, spied.call_count)

    @ddt.data(("70010000000025", False), ("70010000000529", True))
    @ddt.unpack
    def test_sales(self, nsuid, on_sale):
        class MockedResponse:
            status_code = 200

            def json(self):
                return {
                    "personalized": False,
                    "country": "US",
                    "prices": [
                        {
                            "title_id": 70010000000025,
                            "sales_status": "onsale",
                            "regular_price": {
                                "amount": "$59.99",
                                "currency": "USD",
                                "raw_value": "59.99",
                            },
                        },
                        {
                            "title_id": 70010000000529,
                            "sales_status": "onsale",
                            "regular_price": {
                                "amount": "$59.99",
                                "currency": "USD",
                                "raw_value": "59.99",
                            },
                            "discount_price": {
                                "amount": "$41.99",
                                "currency": "USD",
                                "raw_value": "41.99",
                                "start_datetime": "2020-04-30T06:00:00Z",
                                "end_datetime": "2020-05-10T14:59:59Z",
                            },
                        },
                    ],
                }

            def raise_for_status(self):
                pass

        game = noa.game_info(nsuid=nsuid)

        with mock.patch("requests.get") as patched:
            patched.return_value = MockedResponse()
            price = game.price(country="US")

        self.assertEqual(game.nsuid, price.nsuid)
        self.assertFalse(price.is_free_to_play)

        self.assertEqual("US", price.country)
        self.assertEqual("USD", price.currency)
        self.assertEqual(59.99, price.value)

        if not on_sale:
            self.assertEqual("USD 59.99", str(price))
            self.assertEqual(None, price.sale_value)
            self.assertEqual(0, price.sale_discount)
            self.assertFalse(price.is_sale_active)
        else:
            self.assertEqual("USD 41.99*", str(price))
            self.assertEqual(41.99, price.sale_value)
            self.assertEqual(70, price.sale_discount)
            self.assertFalse(price.is_sale_active)
