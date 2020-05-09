import logging
from datetime import datetime
from functools import lru_cache
from typing import Iterator, List, Union, Type

import requests
import xmltodict

from nintendeals.classes import N3DSGame, SwitchGame
from nintendeals.constants import JP

LISTING_URL = "https://www.nintendo.co.jp/data/software/xml/{platform}.xml"

log = logging.getLogger(__name__)


@lru_cache()
def _list_games(
    game_class: Type,
    filename: str
) -> List[Union[N3DSGame, SwitchGame]]:

    url = LISTING_URL.format(platform=filename)
    response = requests.get(url)
    xml = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']

    games = []

    for data in xml:
        game = game_class(
            title=data["TitleName"],
            region=JP,
            nsuid=data["LinkURL"].split("/")[-1],
            product_code=data["InitialCode"],
        )

        game.developer = data.get("MakerName")
        game.free_to_play = data.get("Price") == "無料"

        try:
            game.release_date = datetime.strptime(
                data.get('SalesDate'), '%Y.%m.%d'
            )
        except (ValueError, TypeError):
            game.release_date = None

        games.append(game)

    return games


def list_3ds_games() -> Iterator[N3DSGame]:
    """
        List all the 3DS games in Nintendo of Japan. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * region: str = "JP"
        * platform: str = "Nintendo 3DS"

        * developer: str
        * release_date: datetime (may be None)

        # Features
        * free_to_play: bool

    Yields
    -------
    nintendeals.classes.N3DSGame:
        3DS game from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(N3DSGame, filename="3ds_pkg_dl")


def list_switch_games() -> Iterator[SwitchGame]:
    """
        List all the Switch games in Nintendo of Japan. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * region: str = "JP"
        * platform: str = "Nintendo Switch"

        * developer: str
        * release_date: datetime (may be None)

        # Features
        * free_to_play: bool

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SwitchGame, filename="switch")
