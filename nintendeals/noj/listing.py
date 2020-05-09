import logging
from datetime import datetime
from functools import lru_cache
from typing import Iterator, List

import requests
import xmltodict

from nintendeals.classes.games import Game
from nintendeals.constants import JP, SWITCH, N3DS

LISTING_URL = "https://www.nintendo.co.jp/data/software/xml/{platform}.xml"

FILENAMES = {
    SWITCH: "switch",
    N3DS: "3ds_pkg_dl",
}

log = logging.getLogger(__name__)


@lru_cache()
def _list_games(platform: str) -> List[Game]:
    url = LISTING_URL.format(platform=FILENAMES.get(platform))
    response = requests.get(url)

    games = []
    games_data = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']

    for data in games_data:
        game = Game(
            title=data["TitleName"],
            region=JP,
            platform=platform,
            nsuid=data["LinkURL"].split("/")[-1],
            product_code=data["InitialCode"],
        )

        game.developer = data.get("MakerName")
        game.free_to_play = data.get("Price") == "無料"

        try:
            game.release_date = datetime.strptime(data.get('SalesDate'), '%Y.%m.%d')
        except (ValueError, TypeError):
            game.release_date = None

        games.append(game)

    return games


def list_switch_games() -> Iterator[Game]:
    """
        List all the Switch games in Nintendo of Japan. The following subset
    of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * region: str = "JP"
        * platform: str = "Nintendo Switch"

        * developer: str
        * release_date: datetime (may be None)

        # Common Features
        * free_to_play: bool

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of Switch games from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SWITCH)


def list_3ds_games() -> Iterator[Game]:
    """
        List all the 3DS games in Nintendo of Japan. The following subset
    of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * region: str = "JP"
        * platform: str = "Nintendo 3DS"

        * developer: str
        * release_date: datetime (may be None)

        # Common Features
        * free_to_play: bool

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of 3DS games from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(N3DS)
