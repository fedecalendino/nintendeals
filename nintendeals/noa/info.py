import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nintendeals.classes.games import Game
from nintendeals.constants import NA, PLATFORMS
from nintendeals.noa.external import algolia
from nintendeals.util import unquote

DETAIL_URL = "https://www.nintendo.com/games/detail/{slug}/"


def _aria_label(soup, label, tag="a"):
    tag = soup.find(tag, {"aria-label": label})
    return tag and unquote(tag.text.strip())


def _class(soup, cl, tag="dd"):
    tag = soup.find(tag, {"class": cl})
    return tag and unquote(tag.text.strip())


def _itemprop(soup, prop, tag="dd"):
    tag = soup.find(tag, {"itemprop": prop})
    return tag and unquote(tag.text.strip())


def _scrap(url: str) -> Game:
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.text, features="html.parser")

    script = next(filter(lambda s: "window.game" in str(s), soup.find_all('script')))
    lines = [line.strip().replace("\",", "") for line in str(script).split("\n") if ':' in line]
    data = dict(map(lambda line: line.split(': "'), lines))

    platform = data["platform"]

    game = Game(
        nsuid=data["nsuid"],
        product_code=data["productCode"],
        title=data["title"],
        region=NA,
        platform=PLATFORMS[platform],
    )

    # Genres
    game.genres = unquote(data["genre"]).split(",")
    game.genres.sort()

    # Languages
    game.languages = _class(soup, "languages").split(",")
    game.languages.sort()

    # Players
    try:
        game.players = int(re.sub(r"[^\d]*", "", _class(soup, "num-of-players")))
    except ValueError:
        game.players = 0

    # Release date
    try:
        release_date = _itemprop(soup, "releaseDate")
        game.release_date = datetime.strptime(release_date, '%b %d, %Y')
    except ValueError:
        pass

    # Game size (in MBs)
    game.size, unit = _itemprop(soup, "romSize").split(" ")
    game.size = round(float(game.size) * (1024 if unit == "GB" else 1))

    # Other properties
    game.demo = _aria_label(soup, "Download game demo opens in another window.") is not None
    game.description = _itemprop(soup, "description", tag="div")
    game.developer = _itemprop(soup, "manufacturer")
    game.dlc = _class(soup, "dlc", tag="section") is not None
    game.free_to_play = data["msrp"] == '0'
    game.game_vouchers = _aria_label(soup, "Eligible for Game Vouchers") is not None
    game.online_play = _aria_label(soup, "online-play") is not None
    game.publisher = unquote(data["publisher"])
    game.save_data_cloud = _aria_label(soup, "save-data-cloud") is not None
    game.na_slug = unquote(data["slug"])

    # Unknown
    game.amiibo = None
    game.iaps = None
    game.local_multiplayer = None
    game.voice_chat = None

    return game


def game_info(nsuid: str) -> Game:
    print(f"Fetching slug for {nsuid} in algolia")
    slug = algolia.find_by_nsuid(nsuid)
    print(f"Found slug {slug} for {nsuid}")

    url = DETAIL_URL.format(slug=slug)

    print(f"Getting info of game from {url}")
    return _scrap(url)
