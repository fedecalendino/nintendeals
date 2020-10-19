from typing import Iterator, Optional

import requests
import xmltodict

from nintendeals.constants import (
    NINTENDO_3DS,
    NINTENDO_SWITCH,
    NINTENDO_WII_U,
)

MISSING_URL = "https://www.nintendo.co.jp/missing.html"
SEARCH_URL = "https://search.nintendo.jp/nintendo_soft/search.json"
SOFTWARE_URL = "https://www.nintendo.co.jp/data/software/xml/{filename}.xml"

FILENAMES = {
    NINTENDO_3DS: "3ds_pkg_dl",
    NINTENDO_SWITCH: "switch",
    NINTENDO_WII_U: "wiiu_pkg_dl",
}


def software(platform: str) -> Iterator[dict]:
    response = requests.get(SOFTWARE_URL.format(filename=FILENAMES[platform]))

    if response.status_code != 200:
        return

    if response.url == MISSING_URL:
        return

    yield from xmltodict.parse(response.text)['TitleInfoList']['TitleInfo']


def search(nsuid: str) -> Optional[dict]:
    response = requests.get(url=SEARCH_URL, params={"q": nsuid})

    if response.status_code != 200:
        return None

    items = response.json()["result"]["items"]

    return items[-1] if items else None
