import requests
from bs4 import BeautifulSoup


ESHOP_URL = "https://www.nintendo.com/games/detail/{slug}"


def scrap(slug):
    response = requests.get(
        url=ESHOP_URL.format(slug=slug),
        allow_redirects=True
    )

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, features="html.parser")
    div = soup.find("div", class_="game-details")
    script = div.find("script")

    data = {}
    separator = ': "'

    for line in str(script).split("\n"):
        if separator not in line:
            continue

        key, value = line.strip().split(separator)
        value, _ = value.strip().split('"')

        data[key] = value

    languages = soup.find("dd", class_="languages")

    if languages:
        languages = languages.text.strip().split(", ")
    else:
        languages = ["English"]

    save_data_cloud = soup.find("a", attrs={"aria-label": "save-data-cloud"}) is not None

    return {
        "nsuid": data.get("nsuid"),
        "product_code": data.get("productCode"),
        "slug": data["slug"].replace("\\u002D", "-"),
        "title": data["title"],
        "languages": languages,
        "save_data_cloud": save_data_cloud,
    }
