import logging
from datetime import datetime
from functools import lru_cache
from typing import Iterator, List, Union, Type

import requests
import xmltodict

from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.constants import JP

log = logging.getLogger(__name__)


@lru_cache()
def _list_games(
    game_class: Type,
    filename: str
) -> List[Union[N3dsGame, SwitchGame]]:
    url = f"https://www.nintendo.co.jp/data/software/xml/{filename}.xml"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    xml = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']

    games = []

    for data in xml:
        game = game_class(
            region=JP,
            title=data["TitleName"],
            nsuid=data["LinkURL"].split("/")[-1],
            product_code=data["InitialCode"],
        )

        game.developer = data.get("MakerName")
        game.free_to_play = data.get("Price") == "無料"

        try:
            game.release_date = datetime.strptime(
                data.get('SalesDate'),
                '%Y.%m.%d'
            )
        except (ValueError, TypeError):
            game.release_date = None

        game.banner_img = data.get("ScreenshotImgURL")

        games.append(game)

    return games


def list_3ds_games() -> Iterator[N3dsGame]:
    """
        List all the 3DS games in Nintendo of Japan. The following subset
    of data will be available for each game.

    Game data
    ---------
        * platform: str ["Nintendo 3DS"]
        * region: str ["JP"]
        * title: str
        * nsuid: str
        * product_code: str

        * developer: str
        * free_to_play: bool
        * release_date: datetime (optional)

        * banner_img: str

    Yields
    -------
    nintendeals.classes.N3dsGame:
        3DS game from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(N3dsGame, filename="3ds_pkg_dl")


def list_switch_games() -> Iterator[SwitchGame]:
    """
        List all the Switch games in Nintendo of Japan. The following subset
    of data will be available for each game.

    Game data
    ---------
        * platform: str ["Nintendo Switch"]
        * region: str ["JP"]
        * title: str
        * nsuid: str
        * product_code: str

        * developer: str
        * free_to_play: bool
        * release_date: datetime (optional)

        * banner_img: str

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Japan.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SwitchGame, filename="switch")
