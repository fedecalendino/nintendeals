from typing import Iterator

import requests

from nintendeals.commons.enumerates import Platforms


SEARCH_URL = "https://search.nintendo-europe.com/en/select"

SYSTEM_NAMES = {
    Platforms.NINTENDO_WII_U: "Wii U",
    Platforms.NINTENDO_3DS: "3DS",
    Platforms.NINTENDO_SWITCH: "Switch",
}


def search(platform: Platforms, query: str = "*") -> Iterator[dict]:
    system_name = SYSTEM_NAMES[platform]

    rows = 200
    start = -rows

    while True:
        start += rows

        params = {
            "fq": f'type:GAME AND system_names_txt:"{system_name}"',
            "q": query,
            "rows": rows,
            "sort": "title asc",
            "start": start,
            "wt": "json",
        }

        response = requests.get(url=SEARCH_URL, params=params)

        if response.status_code != 200:
            break

        data = response.json()['response'].get('docs', [])

        if not len(data):
            break

        yield from data
