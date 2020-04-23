# TODO document
from datetime import datetime
from typing import Iterator

import requests
import xmltodict

from nintendeals.classes.games import Game
from nintendeals.constants import JP, SWITCH

LISTING_URL = 'https://www.nintendo.co.jp/data/software/xml/{platform}.xml'

FILENAMES = {
    SWITCH: "switch",
}


def list_games(platform: str) -> Iterator[Game]:
    assert platform in FILENAMES

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
