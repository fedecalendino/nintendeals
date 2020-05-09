import logging
import re
from datetime import datetime
from urllib import parse

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes.games import Game
from nintendeals.constants import NA, PLATFORMS
from nintendeals.noa.external import algolia

DETAIL_URL = "https://www.nintendo.com/games/detail/{slug}"

log = logging.getLogger(__name__)


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

    game.na_slug = _unquote(data["slug"])

    game.description = _itemprop(soup, "description", tag="div")
    game.developer = _itemprop(soup, "manufacturer")
    game.publisher = _unquote(data["publisher"])

    # Genres
    game.genres = list(sorted([
        genre for genre in _unquote(data["genre"]).split(",")
        if genre != "Undefined"
    ]))

    # Languages
    game.languages = _class(soup, "languages")

    if game.languages:
        game.languages = game.languages.split(",")
        game.languages.sort()
    else:
        game.languages = []

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

        if unit.lower() == "blocks":
            game.size = int(game.size) // 8
        else:
            game.size = round(float(game.size) * (1024 if unit == "GB" else 1))

    # Common Features
    game.demo = _aria_label(soup, "Download game demo opens in another window.") is not None
    game.dlc = _class(soup, "dlc", tag="section") is not None
    game.free_to_play = data["msrp"] == '0'
    game.online_play = _aria_label(soup, "online-play") is not None

    # 3DS Features
    game.street_pass = "StreetPass" in game.description
    game.virtual_console = soup.find("img", attrs={"alt": "Virtual Console"}) is not None

    # Switch Features
    game.game_vouchers = _aria_label(soup, "Eligible for Game Vouchers") is not None
    game.save_data_cloud = _aria_label(soup, "save-data-cloud") is not None

    return game


@validate.nsuid
def game_info(*, nsuid: str) -> Game:
    """
        Given an `nsuid` valid for the American region, it will provide the
    information of the game with that nsuid.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str
        * region: str = "NA"
        * na_slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * languages: List[str]
        * publisher: str
        * release_date: datetime
        * size: int

        # Common Features
        * demo: bool
        * dlc: bool
        * free_to_play: bool
        * online_play: bool

        # 3DS Features
        * street_pass: bool
        * virtual_console: bool

        # Switch Features
        * game_vouchers: bool
        * save_data_cloud: bool

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    classes.nintendeals.games.Game:
        Information provided by NoA of the game with the given nsuid.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid was either none or has an invalid format.
    """
    slug = algolia.find_by_nsuid(nsuid)
    url = DETAIL_URL.format(slug=slug)

    log.info("Fetching info for %s from %s", nsuid, url)

    return _scrap(url)
