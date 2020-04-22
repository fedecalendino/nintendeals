from typing import Tuple, Iterator
from nintendeals.constants import SWITCH

import requests


LISTING_URL = 'https://search.nintendo-europe.com/en/select'

SYSTEM_NAMES = {
    SWITCH: "Switch",
}


def list_games(platform: str) -> Iterator[Tuple[str, str]]:
    assert platform in SYSTEM_NAMES
    system_name = SYSTEM_NAMES[platform]

    rows = 200
    start = -rows

    while True:
        start += rows

        params = {
            "q": "*",
            "wt": "json",
            "sort": "title asc",
            "start": start,
            "rows": rows,
            "fq": f"type:GAME AND system_names_txt:\"{system_name}\""
        }

        response = requests.get(url=LISTING_URL, params=params)
        json = response.json().get('response').get('docs', [])

        if not len(json):
            break

        for data in json:
            title = data["title_extras_txt"][0]

            for nsuid in data.get("nsuid_txt", []):
                yield nsuid, title
