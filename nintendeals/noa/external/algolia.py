import logging
from typing import Iterator, Dict

from algoliasearch.search_client import SearchClient

from nintendeals.constants import SWITCH, N3DS

APP_ID = "U3B6GR4UA3"
API_KEY = "c4da8be7fd29f0f5bfa42920b0a99dc7"

INDEX_NAME = "ncom_game_en_us"
INDEX = None


PLATFORM_CODES = {
    SWITCH: "7001",
    N3DS: "5001",
}

log = logging.getLogger(__name__)


def _search_index(query, **options):
    global INDEX

    if not INDEX:
        client = SearchClient.create(APP_ID, API_KEY)
        INDEX = client.init_index(INDEX_NAME)

    log.info("Searching index for %s", query)

    response = INDEX.search(query, request_options=options)
    return response.get('hits', [])


def _search_by_nsuid(platform: str) -> Iterator[Dict]:
    empty_pages = 0

    platform_code = PLATFORM_CODES[platform]

    options = {
        "allowTyposOnNumericTokens": False,
        "queryType": "prefixAll",
        "restrictSearchableAttributes": ["nsuid"],
        "facetFilters": [
            f"platform:{platform}"
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


def _search_by_query(platform: str, query: str) -> Iterator[Dict]:
    hits_per_page = 50

    options = {
        "facetFilters": [
            f"platform:{platform}"
        ],
        "hitsPerPage": hits_per_page,
    }

    page = -1
    while True:
        page += 1
        options["page"] = page

        games = _search_index(query, **options)

        yield from games

        if len(games) < hits_per_page:
            break


def search_games(platform: str, **kwargs) -> Iterator[Dict]:
    query = kwargs.get("query")

    if query:
        yield from _search_by_query(platform, query)
    else:
        yield from _search_by_nsuid(platform)


def find_by_nsuid(nsuid: str) -> str:
    hits = _search_index(
        nsuid,
        attributesToRetrieve=["title", "nsuid", "slug"],
        restrictSearchableAttributes=['nsuid'],
    )

    return (hits or [{}])[0].get("slug")
