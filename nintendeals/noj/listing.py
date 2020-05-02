import logging
from datetime import datetime
from functools import lru_cache
from typing import Iterator, List

import requests
import xmltodict

from nintendeals.classes.games import Game
from nintendeals.constants import JP, SWITCH

LISTING_URL = "https://www.nintendo.co.jp/data/software/xml/{platform}.xml"

FILENAMES = {
    SWITCH: "switch",
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
        List all the games in Nintendo of Japan. A subset of data
    will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str = "Nintendo Switch"
        * region: str = "JP"

        * developer: str
        * free_to_play: bool
        * release_date: datetime (may be None)

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of games from Nintendo of Japan.
    """
    log.info("Fetching list of nintendo switch games")

    yield from _list_games(SWITCH)
