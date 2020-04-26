import json

from algoliasearch.search_client import SearchClient

from nintendeals.constants import SWITCH
from nintendeals.exceptions import UnsupportedPlatform

APP_ID = "U3B6GR4UA3"
API_KEY = "9a20c93440cf63cf1a7008d75f7438bf"

INDEX_NAME = "noa_aem_game_en_us_title_asc"
INDEX = None


PLATFORM_CODES = {
    SWITCH: "7001"
}


def _search_index(query, **options):
    global INDEX

    if not INDEX:
        client = SearchClient.create(APP_ID, API_KEY)
        INDEX = client.init_index(INDEX_NAME)

    response = INDEX.search(query, request_options=options)
    return response.get('hits', [])


def find_by_nsuid(nsuid: str) -> str:
    hits = _search_index(
        nsuid,
        attributesToRetrieve=["title", "nsuid", "slug"],
        restrictSearchableAttributes=['nsuid'],
    )

    return hits[0]["slug"]


def search_games(platform: str) -> json:
    try:
        platform_code = PLATFORM_CODES[platform]

    except KeyError:
        raise UnsupportedPlatform(platform)

    options = {
        "allowTyposOnNumericTokens": False,
        "facetFilters": [
            f"platform:{platform}"
        ],
        "hitsPerPage": 500,
        'queryType': 'prefixAll',
        'restrictSearchableAttributes': ['nsuid'],
    }

    current = -1

    while True:
        current += 1
        query = f"{platform_code}{current:07}"
        games = _search_index(query, **options)

        if not games:
            break

        yield from games
