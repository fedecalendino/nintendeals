import json

import requests
from bs4 import BeautifulSoup

ESHOP_URL = "https://www.nintendo.com/store/products/{slug}/"


def scrap(slug):
    url = ESHOP_URL.format(slug=slug)
    response = requests.get(url, allow_redirects=True)

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, features="html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    data = json.loads(script.text)["props"]["pageProps"]["product"]

    h3 = soup.find("h3", text="Supported languages")
    languages = next(h3.nextSiblingGenerator())

    if languages:
        languages = languages.text.strip().split(", ")
    else:
        languages = ["English"]

    nso_features = {feature["code"] for feature in data["nsoFeatures"]}

    return {
        "nsuid": data.get("nsuid"),
        "product_code": data.get("productCode"),
        "slug": data["urlKey"],
        "title": data["name"],
        "languages": languages,
        "save_data_cloud": "SAVE_DATA_CLOUD" in nso_features,
    }
