import logging
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Tuple

import requests
from dateutil.parser import parse as date_parser

from nintendeals import validate
from nintendeals.classes.prices import Price

log = logging.getLogger(__name__)


def _parse_date(string: str) -> datetime:
    return date_parser(string).replace(tzinfo=None)


@validate.country
@validate.nsuids
def _fetch_prices(
    *,
    country: str,
    nsuids: List[str]
) -> Dict[str, Price]:
    if not 51 > len(nsuids) > 0:
        raise ValueError("The amount of nsuids must between 1 and 50.")

    log.info("Calling prices api with %i nsuids", len(nsuids))

    response = requests.get(
        url="https://api.ec.nintendo.com/v1/price",
        params=dict(
            country=country,
            lang="en",
            ids=",".join(nsuids),
        )
    )

    response.raise_for_status()

    total = 0
    sales = 0
    prices = {}

    for data in response.json().get('prices', []):
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


@validate.country
@validate.games
def get_prices(
    *,
    country: str,
    games: List["Game"]
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
        Any of the `games` had an nsuid that is either none or
    has an invalid format.
    """
    log.info("Fetching prices for %i games in %s", len(games), country)

    prices = {}
    chunk = []

    for game in games:
        chunk.append(game)

        if len(chunk) == 50:
            nsuids = [game.nsuid for game in chunk]
            fetched = _fetch_prices(country=country, nsuids=nsuids)
            prices.update(fetched)

            chunk = []

    if chunk:
        nsuids = [game.nsuid for game in chunk if game.nsuid]
        fetched = _fetch_prices(country=country, nsuids=nsuids)
        prices.update(fetched)

    yield from prices.items()


@validate.country
@validate.game
def get_price(
    *,
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
    game: nintendeals.classes.games.Game
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
        The nsuid was either none or has an invalid format.
    """
    log.info("Fetching price for %s games in %s", game.title, country)

    fetched = _fetch_prices(country=country, nsuids=[game.nsuid])
    return fetched.get(game.nsuid)
