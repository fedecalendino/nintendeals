from typing import Iterator

import requests

from nintendeals.constants import (
    NINTENDO_3DS,
    NINTENDO_SWITCH,
    NINTENDO_WII_U,
)


SEARCH_URL = "https://search.nintendo-europe.com/en/select"

SYSTEM_NAMES = {
    NINTENDO_3DS: "3DS",
    NINTENDO_SWITCH: "Switch",
    NINTENDO_WII_U: "Wii U",
}


def search(platform: str, query: str = "*") -> Iterator[dict]:
    rows = 200
    start = -rows

    while True:
        start += rows

        params = {
            "fq": f'type:GAME AND system_names_txt:"{SYSTEM_NAMES[platform]}"',
            "q": query,
            "rows": rows,
            "sort": "title asc",
            "start": start,
            "wt": "json",
        }

        response = requests.get(url=SEARCH_URL, params=params)

        if response.status_code != 200:
            break

        json = response.json()['response'].get('docs', [])

        if not len(json):
            break

        yield from json
