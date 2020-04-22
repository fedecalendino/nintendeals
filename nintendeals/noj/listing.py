from typing import Iterator, Tuple
from nintendeals.constants import SWITCH

import requests
import xmltodict


LISTING_URL = 'https://www.nintendo.co.jp/data/software/xml/{platform}.xml'

FILENAMES = {
    SWITCH: "switch",
}


def list_games(platform: str) -> Iterator[Tuple[str, str]]:
    assert platform in FILENAMES

    url = LISTING_URL.format(platform=FILENAMES.get(platform))
    response = requests.get(url)

    games = xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']

    yield from map(
        lambda game: (game["LinkURL"].split("/")[-1], game["TitleName"]),
        games
    )

