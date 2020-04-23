from typing import Dict, List, Iterable

import requests
from dateutil.parser import parse as date_parser
from pycountry import countries

from nintendeals.classes.prices import Price

PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={ids}'


def _fetch_prices(country: str, nsuids: List[str]) -> Dict[str, Price]:
    assert countries.get(alpha_2=country)
    assert 51 > len(nsuids) > 0

    print(f"Fetching prices on {country} for {len(nsuids)} nsuids")

    url = PRICE_API.format(country=country, ids=','.join(nsuids))
    response = requests.get(url)
    json = response.json()

    prices = {}
    found = 0
    sales = 0

    for data in json['prices']:
        nsuid = str(data["title_id"])
        regular_price = data.get("regular_price")

        if not regular_price:
            prices[nsuid] = None
            continue

        found += 1

        price = Price(
            nsuid=nsuid,
            country=country,
            currency=regular_price["currency"],
            value=float(regular_price["raw_value"]),
        )

        discount_price = data.get("discount_price")

        if discount_price:
            price.sale_value = float(discount_price["raw_value"])
            price.sale_start = date_parser(discount_price['start_datetime']).replace(tzinfo=None)
            price.sale_end = date_parser(discount_price['end_datetime']).replace(tzinfo=None)

            sales += 1

        prices[price.nsuid] = price

    print(f" * Found {found} prices and {sales} sales")
    return prices


def get_prices(country: str, games: Iterable["Game"]) -> Dict[str, Price]:
    assert country
    assert games

    size = 50

    prices = {}
    chunk = []
    for game in games:
        chunk.append(game)

        if len(chunk) == size:
            nsuids = [game.nsuid for game in chunk if game.nsuid]
            prices.update(_fetch_prices(country, nsuids))

            chunk = []

    if chunk:
        nsuids = [game.nsuid for game in chunk if game.nsuid]
        prices.update(_fetch_prices(country, nsuids))

    return prices


def get_price(country: str, game: "Game") -> Price:
    assert country
    assert game.nsuid

    return _fetch_prices(country, [game.nsuid]).get(game.nsuid)
