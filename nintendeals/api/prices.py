import logging
from datetime import datetime
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import requests
from dateutil.parser import parse as date_parser

from nintendeals import validate
from nintendeals.classes.prices import Price

PRICE_API_URL = 'https://api.ec.nintendo.com/v1/price'

log = logging.getLogger(__name__)


def _parse_date(string) -> datetime:
    return date_parser(string).replace(tzinfo=None)


def _fetch_prices(
    country: str,
    nsuids: List[str]
) -> Dict[str, Price]:
    if not 51 > len(nsuids) > 0:
        raise ValueError("The amount of nsuids must between 1 and 50.")

    validate.alpha_2(country)
    list(map(validate.nsuid_format, nsuids))

    log.info("Fetching prices for %i nsuids in %s", len(nsuids), country)

    response = requests.get(
        url=PRICE_API_URL,
        params={
            "country": country,
            "lang": "en",
            "ids": ",".join(nsuids)
        }
    )

    json = response.json()

    total = 0
    sales = 0
    prices = {}

    for data in json['prices']:
        nsuid = str(data["title_id"])
        regular_price = data.get("regular_price")

        if not regular_price:
            prices[nsuid] = None
            continue

        total += 1

        price = Price(
            nsuid=nsuid,
            country=country,
            currency=regular_price["currency"],
            value=float(regular_price["raw_value"]),
        )

        discount_price = data.get("discount_price")

        if discount_price:
            price.sale_value = float(discount_price["raw_value"])
            price.sale_start = _parse_date(discount_price['start_datetime'])
            price.sale_end = _parse_date(discount_price['end_datetime'])

            sales += 1

        prices[price.nsuid] = price

    log.info("Found %i prices and %i sales", total, sales)

    return prices


def get_prices(
    country: str,
    games: Iterable["Game"]
) -> Iterator[Tuple[str, Price]]:
    """
        Given a valid `country` code and a list of `games` (each with a nsuid)
    it will retrieve the current pricing of those games for that country.

    Parameters
    ----------
    country: str
        Valid alpha-2 code of the country.
    games: List[nintendeals.classes.games.Game]
        Games to get their pricing.

    Yields
    -------
    Tuple[str, nintendeals.classes.prices.Price]
        Dictionary containing the nsuids as keys and each pricing as value.

    Raises
    -------
    nintendeals.exceptions.InvalidAlpha2Code
        The `country` wasn't a valid alpha-2 code.
    nintendeals.exceptions.InvalidNsuidFormat
        Any of the `games` had an nsuid that was either none or invalid.
    """
    validate.alpha_2(country)
    games = list(filter(lambda g: g.nsuid, games))

    log.info("Fetching prices for %i games in %s", len(games), country)

    prices = {}
    chunk = []

    for game in games:
        chunk.append(game)

        if len(chunk) == 50:
            nsuids = [game.nsuid for game in chunk if game.nsuid]
            prices.update(_fetch_prices(country, nsuids))

            chunk = []

    if chunk:
        nsuids = [game.nsuid for game in chunk if game.nsuid]
        prices.update(_fetch_prices(country, nsuids))

    yield from prices.items()


def get_price(
    country: str,
    game: "Game"
) -> Optional[Price]:
    """
        Given a valid `country` code and a `game` (with an nsuid) it will
    retrieve the current pricing of that game for that country.

    Parameters
    ----------
    country: str
        Valid alpha-2 code of the country.
    game
        Game to get its pricing.

    Returns
    -------
    nintendeals.classes.prices.Price
        Pricing of the game in the indicated country.

    Raises
    -------
    nintendeals.exceptions.InvalidAlpha2Code
        The `country` wasn't a valid alpha-2 code.
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid of the `game` was either none or invalid.
    """
    validate.alpha_2(country)
    validate.nsuid_format(game.nsuid)

    log.info("Fetching price for %s games in %s", game.title, country)

    prices = _fetch_prices(country, [game.nsuid])
    return prices.get(game.nsuid)
