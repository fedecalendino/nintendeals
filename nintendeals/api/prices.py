from datetime import datetime
from typing import Iterable, Iterator, Optional, Tuple

import requests
from dateutil.parser import parse as date_parser

from nintendeals.commons.classes.prices import Price


def _parse_date(string: str) -> datetime:
    return date_parser(string).replace(tzinfo=None)


def fetch_prices(
    country: str,
    nsuids: Iterable[str]
) -> Iterator[Tuple[str, Price]]:
    nsuids = set(nsuids)

    if not 51 > len(nsuids) > 0:
        raise ValueError("The amount of nsuids must between 1 and 50.")

    response = requests.get(
        url="https://api.ec.nintendo.com/v1/price",
        params=dict(
            country=country,
            lang="en",
            ids=",".join(nsuids),
        )
    )

    response.raise_for_status()

    for data in response.json().get('prices', []):
        nsuid = str(data["title_id"])
        regular_price = data.get("regular_price")

        if not regular_price:
            continue

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

        yield price.nsuid, price


def get_prices(games: Iterable["Game"], country: str) -> Iterator[Tuple[str, Price]]:
    """
    Given an iterable of `games` (each with a nsuid) and a valid `country` code
    it will retrieve the current pricing of those games for that country.

    Parameters
    ----------
    games: Iterable[nintendeals.commons.classes.games.Game]
        Games to get their pricing.
    country: str
        Valid alpha-2 code of the country.

    Yields
    -------
    Tuple[str, nintendeals.commons.classes.prices.Price]
        Dictionary containing the nsuids as keys and each pricing as value.
    """
    prices = {}
    chunk = []

    for game in games:
        chunk.append(game)

        if len(chunk) == 50:
            fetched = {
                nsuid: price for nsuid, price in
                fetch_prices(
                    country=country,
                    nsuids=[game.nsuid for game in chunk]
                )
            }
            prices.update(fetched)

            chunk = []

    if chunk:
        fetched = {
            nsuid: price for nsuid, price in
            fetch_prices(
                country=country,
                nsuids=[game.nsuid for game in chunk]
            )
        }
        prices.update(fetched)

    yield from prices.items()


def get_price(game: "Game", country: str) -> Optional[Price]:
    """
    Given a `game` (with an nsuid) and a valid `country` code it will retrieve
    the current pricing of that game for that country.

    Parameters
    ----------
    game: nintendeals.commons.classes.games.Game
        Game to get its pricing.
    country: str
        Valid alpha-2 code of the country.

    Returns
    -------
    nintendeals.classes.commons.prices.Price
        Pricing of the game in the indicated country.
    """
    fetched = {
        nsuid: price
        for nsuid, price in fetch_prices(country=country, nsuids=[game.nsuid])
    }

    return fetched.get(game.nsuid)
