from typing import Iterator, Optional

import requests

from nintendeals.commons.enumerates import Platforms

SEARCH_URL = "https://search.nintendo-europe.com/en/select"

SYSTEM_NAMES = {
    Platforms.NINTENDO_3DS: "3DS",
    Platforms.NINTENDO_SWITCH: "Switch",
    Platforms.NINTENDO_WIIU: "Wii U",
}


def _search(
        query: str = "*",
        nsuid: str = None,
        platform: Platforms = None
) -> Iterator[dict]:
    rows = 200

    params = {
        "fq": "type:GAME",
        "q": query,
        "rows": rows,
        "sort": "title asc",
        "start": -rows,
        "wt": "json",
    }

    if platform:
        system_name = SYSTEM_NAMES[platform]
        params["fq"] += f' AND system_names_txt:"{system_name}"'

    if nsuid:
        params["fq"] += f' AND nsuid_txt:"{nsuid}"'

    while True:
        params["start"] += rows
        response = requests.get(url=SEARCH_URL, params=params)

        if response.status_code != 200:
            break

        data = response.json()['response'].get('docs', [])

        if not len(data):
            break

        yield from data


def search_by_nsuid(nsuid: str) -> Optional[dict]:
    try:
        return next(_search(nsuid=nsuid))
    except StopIteration:
        return None


def search_by_platform(platform: Platforms) -> Iterator[dict]:
    yield from _search(platform=platform)


def search_by_query(query: str, platform: Platforms = None) -> Iterator[dict]:
    yield from _search(query=query, platform=platform)
