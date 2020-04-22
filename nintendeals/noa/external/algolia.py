import json
from string import ascii_lowercase, digits

from nintendeals.constants import PLATFORMS
from algoliasearch.search_client import SearchClient

APP_ID = "U3B6GR4UA3"
API_KEY = "9a20c93440cf63cf1a7008d75f7438bf"

INDEX_NAME = "noa_aem_game_en_us"

client = SearchClient.create(APP_ID, API_KEY)
index = client.init_index(INDEX_NAME)


def _search_index(query, **options):
    response = index.search(query, request_options=options)
    return response.get('hits', [])


def find_by_nsuid(nsuid: str) -> str:
    hits = _search_index(
        nsuid,
        attributesToRetrieve=["title", "nsuid", "slug"]
    )

    return hits[0]["slug"]


def search_games(platform: str, query: str) -> json:
    assert platform in PLATFORMS

    hits_per_page = 500

    options = {
        "attributesToRetrieve": ["title", "nsuid"],
        "hitsPerPage": hits_per_page,
        "facetFilters": [
            f"platform:{platform}"
        ]
    }

    page = -1

    while True:
        page += 1
        games = _search_index(
            query,
            page=page,
            **options
        )

        if not games:
            break

        for game in games:
            nsuid = game.get("nsuid")

            if not nsuid:
                continue

            yield nsuid, game["title"]

        if len(games) < hits_per_page:
            break
