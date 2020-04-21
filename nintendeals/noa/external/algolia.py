import requests

APP_ID = "u3b6gr4ua3"
API_KEY = "9a20c93440cf63cf1a7008d75f7438bf"

URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/noa_aem_game_en_us"

HEADERS = {
  "X-Algolia-API-Key": API_KEY,
  "X-Algolia-Application-Id": APP_ID.upper(),
}


def query_noa_game_index(nsuid: str) -> str:
    params = {
        "page": 0,
        "hitsPerPage": 1,
        "query": nsuid
    }

    response = requests.get(URL, params=params, headers=HEADERS)
    hit = response.json()["hits"][0]

    assert hit["nsuid"] == nsuid

    return hit["url"].split("/")[-1]
