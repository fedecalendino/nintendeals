import logging
from typing import Dict, List

import requests
from dateutil.parser import parse as date_parser
from pycountry import countries

from nintendeals.classes.prices import Price

PRICE_API = 'https://api.ec.nintendo.com/v1/price?country={country}&lang=en&ids={ids}'

LOG = logging.getLogger('nintendeals.prices')


def get_prices(country: str, nsuids: List[str]) -> Dict[str, Price]:
    country = countries.get(alpha_2=country)
    assert country
    assert 50 > len(nsuids) > 0

    url = PRICE_API.format(country=country.alpha_2, ids=','.join(nsuids))
    response = requests.get(url)
    json = response.json()

    prices = {}

    for data in json['prices']:
        regular_price = data["regular_price"]

        price = Price(
            nsuid=str(data["title_id"]),
            country=country.alpha_2,
            currency=regular_price["currency"],
            value=float(regular_price["raw_value"]),
        )

        discount_price = data.get("discount_price")

        if discount_price:
            price.sale_value = float(discount_price["raw_value"])
            price.sale_start = date_parser(discount_price['start_datetime']).replace(tzinfo=None)
            price.sale_end = date_parser(discount_price['end_datetime']).replace(tzinfo=None)

        prices[price.nsuid] = price

    return prices


def get_price(country: str, nsuid: str) -> Price:
    assert country
    assert nsuid

    return get_prices(country, nsuid).get(nsuid)
