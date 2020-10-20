import requests
from bs4 import BeautifulSoup


URL = "https://www.nintendo.com/games/detail/{slug}"


def scrap(slug):
    response = requests.get(URL.format(slug=slug), allow_redirects=True)

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

    return {
        "nsuid": data["nsuid"],
        "product_code": data["productCode"],
        "slug": data["slug"].replace("\\u002D", "-"),
        "title": data["title"],
    }
