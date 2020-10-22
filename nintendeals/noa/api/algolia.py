from typing import Iterator, Optional

from algoliasearch.search_client import SearchClient

from nintendeals.commons.enumerates import Platforms

APP_ID = "U3B6GR4UA3"
API_KEY = "c4da8be7fd29f0f5bfa42920b0a99dc7"

INDEX_NAME = "ncom_game_en_us"
INDEX = None


PLATFORMS = {
    Platforms.NINTENDO_3DS: "Nintendo 3DS",
    Platforms.NINTENDO_SWITCH: "Nintendo Switch",
    Platforms.NINTENDO_WIIU: "Wii U",
}

PLATFORM_CODES = {
    Platforms.NINTENDO_3DS: "5001",
    Platforms.NINTENDO_SWITCH: "7001",
    Platforms.NINTENDO_WIIU: "Wii U",
}


def _search_index(query, **options):
    global INDEX

    if not INDEX:
        client = SearchClient.create(APP_ID, API_KEY)
        INDEX = client.init_index(INDEX_NAME)

    response = INDEX.search(query, request_options=options)
    return response.get('hits', [])


def search_by_nsuid(nsuid: str) -> Optional[dict]:
    hits = _search_index(nsuid, restrictSearchableAttributes=['nsuid'])
    return (hits or [{}])[0]


def search_by_platform(platform: Platforms) -> Iterator[dict]:
    empty_pages = 0

    platform_code = PLATFORM_CODES[platform]

    options = {
        "allowTyposOnNumericTokens": False,
        "queryType": "prefixAll",
        "restrictSearchableAttributes": ["nsuid"],
        "facetFilters": [
            f"platform:{PLATFORMS[platform]}"
        ],
        "hitsPerPage": 500,
    }

    current = -1

    while True:
        current += 1
        query = f"{platform_code}{current:07}"
        games = _search_index(query, **options)

        if not games:
            empty_pages += 1

        if empty_pages == 5:
            break

        yield from games


def search_by_query(query: str, platform: Platforms = None) -> Iterator[dict]:
    hits_per_page = 50

    options = {
        "hitsPerPage": hits_per_page,
    }

    if platform:
        options["facetFilters"] = [
            f"platform:{PLATFORMS[platform]}"
        ]

    page = -1

    while True:
        page += 1
        options["page"] = page

        games = _search_index(query, **options)

        yield from games

        if len(games) < hits_per_page:
            break
