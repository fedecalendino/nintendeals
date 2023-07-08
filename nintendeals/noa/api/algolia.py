from typing import Iterator, Optional

from algoliasearch.search_client import SearchClient

from nintendeals.commons.enumerates import Platforms

APP_ID = "U3B6GR4UA3"
API_KEY = "a29c6927638bfd8cee23993e51e721c9"

INDEX_NAME = "store_game_en_us"
INDEX = None


PLATFORMS = {
    Platforms.NINTENDO_SWITCH: "Nintendo Switch",
}

PLATFORM_CODES = {
    Platforms.NINTENDO_SWITCH: "7001",
}


def _search_index(query, **options):
    global INDEX

    if not INDEX:
        client = SearchClient.create(APP_ID, API_KEY)
        INDEX = client.init_index(INDEX_NAME)

    response = INDEX.search(query, request_options=options)
    return response.get("hits", [])


def search_by_nsuid(nsuid: str) -> Optional[dict]:
    hits = _search_index(nsuid, restrictSearchableAttributes=["nsuid"])
    return (hits or [{}])[0]


def search_by_platform(platform: Platforms) -> Iterator[dict]:
    empty_pages = 0

    platform_code = PLATFORM_CODES[platform]

    options = {
        "allowTyposOnNumericTokens": False,
        "queryType": "prefixAll",
        "restrictSearchableAttributes": ["nsuid"],
        "hitsPerPage": 500,
    }

    current = -1

    while True:
        current += 1
        query = f"{platform_code}{current:07}"
        items = _search_index(query, **options)

        if not items:
            empty_pages += 1

        if empty_pages == 5:
            break

        for item in items:
            if item["platform"] != platform:
                continue

            yield item


def search_by_query(query: str, platform: Platforms = None) -> Iterator[dict]:
    hits_per_page = 50

    options = {
        "hitsPerPage": hits_per_page,
    }

    page = -1

    while True:
        page += 1
        options["page"] = page

        items = _search_index(query, **options)

        for item in items:
            if item["topLevelCategoryCode"] != "GAMES":
                continue

            if platform:
                if item["platform"] != platform:
                    continue

            yield item

        if len(items) < hits_per_page:
            break
