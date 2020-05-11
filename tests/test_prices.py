from unittest import mock, TestCase

import ddt

from nintendeals import noa
from nintendeals.api import prices
from tests.util import spy


@ddt.ddt
class TestPrices(TestCase):

    def test_prices(self):
        data = {
            "50010000000541": 19.99,  # Ocarina of Time (3DS/Select)
            "50010000006866":  5.99,  # Link's Awakening DX (3DS/VC)
            "50010000007271":  4.99,  # The Legend of Zelda (3DS/VC)
            "50010000007276":  4.99,  # The Adventure of Link (3DS/VC)
            "50010000014332":  5.99,  # Oracle of Ages (3DS/VC)
            "50010000014333":  5.99,  # Oracle of Seasons (3DS/VC)
            "50010000017216": 19.99,  # A Link Between Worlds (3DS/Select)
            "50010000027796": 19.99,  # Majora's Mask (3DS/Select)
            "50010000036995": 39.99,  # Tri Force Heroes (3DS)
            "50010000039719":  7.99,  # A Link to the Past (3DS/VC)
            "70010000000025": 59.99,  # Breath of the Wild (Switch)
            "70010000020033": 59.99,  # Link's Awakening (Switch)
        }

        games = [noa.game_info(nsuid=nsuid) for nsuid in data]

        with spy(prices, "_fetch_prices") as spied:
            for game in games:
                price = game.price(country="US")
                expected_price = data[game.nsuid]

                self.assertIn(price.nsuid, data)
                self.assertEqual("US", price.country)
                self.assertEqual("USD", price.currency)
                self.assertEqual(expected_price, price.value)

            self.assertEqual(len(games), spied.call_count)

        # Testing price fetching in bulk
        with spy(prices, "_fetch_prices") as spied:
            for nsuid, price in prices.get_prices(games=games, country="US"):
                self.assertIn(nsuid, data)
                self.assertIn(price.nsuid, data)

                expected_price = data[nsuid]

                self.assertEqual("US", price.country)
                self.assertEqual("USD", price.currency)
                self.assertEqual(expected_price, price.value)

            self.assertEqual(1, spied.call_count)

    def test_non_existent_prices(self):
        data = [
            "50010000000000",
            "60010000000000",
            "70010000000000"
        ]

        found = prices._fetch_prices(nsuids=data, country="US")
        for nsuid, price in found.items():
            self.assertIn(nsuid, data)
            self.assertIsNone(price)

    def test_fetch_prices_nsuid_limit(self):
        nsuid = "70010000000025"
        nsuids = [nsuid] * 51

        with self.assertRaises(ValueError) as context:
            prices._fetch_prices(nsuids=nsuids, country="US")

            self.assertEqual(
                "The amount of nsuids must between 1 and 50.",
                str(context.exception)
            )

    def test_get_prices_chunks(self):
        nsuid = "70010000000025"
        game = noa.game_info(nsuid=nsuid)

        games = [game] * 222

        with spy(prices, "_fetch_prices") as spied:
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
                                "raw_value": "59.99"
                            },
                        },
                        {
                            "title_id": 70010000000529,
                            "sales_status": "onsale",
                            "regular_price": {
                                "amount": "$59.99",
                                "currency": "USD",
                                "raw_value": "59.99"
                            },
                            "discount_price": {
                                "amount": "$41.99",
                                "currency": "USD",
                                "raw_value": "41.99",
                                "start_datetime": "2020-04-30T06:00:00Z",
                                "end_datetime": "2020-05-10T14:59:59Z"
                            }
                        }
                    ]
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
