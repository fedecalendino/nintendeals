from datetime import datetime
from typing import Iterator

import requests
import xmltodict

from nintendeals.classes.games import Game
from nintendeals.exceptions import UnsupportedPlatform
from nintendeals.constants import JP, SWITCH

LISTING_URL = 'https://www.nintendo.co.jp/data/software/xml/{platform}.xml'

FILENAMES = {
    SWITCH: "switch",
}


def list_games(platform: str) -> Iterator[Game]:
    """
        Given a supported platform it will provide an iterator
    of with a subset of data for all games found in the listing
    service Nintendo of Japan.

    Game data
    ---------
        * title: str
        * region: str (JP)
        * platform: str
        * nsuid: str
        * product_code: str

        * developer: str
        * free_to_play: bool
        * release_date: datetime

    Parameters
    ----------
    platform: str
        Valid nintendo platform.

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Partial information of a game provided by NoJ.
    """
    if not platform in FILENAMES: raise UnsupportedPlatform(platform)

    url = LISTING_URL.format(platform=FILENAMES.get(platform))
    response = requests.get(url)

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
        except:
            return None

        yield game
