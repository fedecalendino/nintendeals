import re
from datetime import datetime
from urllib import parse

import requests
from bs4 import BeautifulSoup

from nintendeals.classes.games import Game
from nintendeals.constants import NA, PLATFORMS
from nintendeals.noa.external import algolia

DETAIL_URL = "https://www.nintendo.com/games/detail/{slug}/"


def _unquote(string: str) -> str:
    return parse.unquote(
        string
        .replace("\\u00", "%")
        .replace("\\x27", "'")
        .replace("\\/", "/")
        .replace(" : ", ": ")
        .strip()
    )


def _aria_label(soup, label, tag="a"):
    tag = soup.find(tag, {"aria-label": label})
    return tag and _unquote(tag.text.strip())


def _class(soup, cl, tag="dd"):
    tag = soup.find(tag, {"class": cl})
    return tag and _unquote(tag.text.strip())


def _itemprop(soup, prop, tag="dd"):
    tag = soup.find(tag, {"itemprop": prop})
    return tag and _unquote(tag.text.strip())


def _scrap(url: str) -> Game:
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.text, features="html.parser")

    scripts = list(filter(lambda s: "window.game" in str(s), soup.find_all('script')))

    if not scripts:
        return None

    script = scripts[0]
    lines = [line.strip().replace("\",", "") for line in str(script).split("\n") if ':' in line]
    data = dict(map(lambda line: line.split(': "'), lines))

    platform = data["platform"]

    game = Game(
        nsuid=data["nsuid"],
        product_code=data["productCode"],
        title=_unquote(data["title"]),
        region=NA,
        platform=PLATFORMS[platform],
    )

    # Genres
    game.genres = _unquote(data["genre"]).split(",")
    game.genres.sort()

    # Languages
    game.languages = _class(soup, "languages").split(",")
    game.languages.sort()

    # Players
    try:
        game.players = int(re.sub(r"[^\d]*", "", _class(soup, "num-of-players")))
    except (ValueError, TypeError):
        game.players = 0

    # Release date
    try:
        release_date = _itemprop(soup, "releaseDate")
        game.release_date = datetime.strptime(release_date, '%b %d, %Y')
    except ValueError:
        pass

    # Game size (in MBs)
    game.size = _itemprop(soup, "romSize")
    if game.size:
        game.size, unit = game.size.split(" ")
        game.size = round(float(game.size) * (1024 if unit == "GB" else 1))

    # Other properties
    game.demo = _aria_label(soup, "Download game demo opens in another window.") is not None
    game.description = _itemprop(soup, "description", tag="div")
    game.developer = _itemprop(soup, "manufacturer")
    game.dlc = _class(soup, "dlc", tag="section") is not None
    game.free_to_play = data["msrp"] == '0'
    game.game_vouchers = _aria_label(soup, "Eligible for Game Vouchers") is not None
    game.online_play = _aria_label(soup, "online-play") is not None
    game.publisher = _unquote(data["publisher"])
    game.save_data_cloud = _aria_label(soup, "save-data-cloud") is not None
    game.na_slug = _unquote(data["slug"])

    # Unknown
    game.amiibo = None
    game.iaps = None
    game.local_multiplayer = None
    game.voice_chat = None

    return game


def game_info(nsuid: str) -> Game:
    """
        Given an `nsuid` valid for the American region, it will provide the
    information of the game with that nsuid.

    Game data
    ---------
        * title: str
        * region: str (NAs)
        * platform: str
        * nsuid: str
        * product_code: str

        * demo: bool
        * description: str
        * developer: str
        * dlc: bool
        * free_to_play: bool
        * genres: List[str]
        * languages: List[str]
        * na_slug: str
        * online_play: bool
        * players: int
        * publisher: str
        * release_date: datetime
        * save_data_cloud: bool
        * size: int
        * game_vouchers: bool

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    classes.nintendeals.games.Game:
        Information provided by NoA of the game with the given nsuid.
    """
    slug = algolia.find_by_nsuid(nsuid)
    url = DETAIL_URL.format(slug=slug)

    return _scrap(url)
