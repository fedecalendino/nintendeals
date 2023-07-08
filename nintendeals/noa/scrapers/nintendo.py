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
    props = json.loads(script.text)["props"]["pageProps"]

    sku = props["linkedData"]["sku"]

    store_product = props["initialApolloState"][f'StoreProduct:{{"sku":"{sku}","locale":"en_US"}}']

    return {
        "slug": store_product["urlKey"],
        "title": store_product["name"],
        "nsuid": store_product["nsuid"],
        "product_code": store_product["productCode"],
        "languages": store_product["supportedLanguages"],
        "players": max(
            store_product.get("playersMaxLocal") or 1,
            store_product.get("playersMaxOnline") or 1,
        ),
        "dlc": len(store_product['relatedProducts({"limit":5})']) > 0,
    }
