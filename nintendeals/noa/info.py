import logging
import re
from datetime import datetime
from typing import Type, Union
from urllib import parse

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.classes.games import Game
from nintendeals.constants import NA, N3DS, SWITCH
from nintendeals.noa.external import algolia

BASE = "https://www.nintendo.com"

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


def _scrap(
    game_class: Type,
    slug: str
) -> Union[N3dsGame, SwitchGame]:
    url = f"https://www.nintendo.com/games/detail/{slug}"
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.text, features="html.parser")

    scripts = list(filter(lambda s: "window.game" in str(s), soup.find_all('script')))

    if not scripts:
        return None

    script = scripts[0]
    lines = [line.strip().replace("\",", "") for line in str(script).split("\n") if ':' in line]
    data = dict(map(lambda line: line.split(': "'), lines))

    game = game_class(
        region=NA,
        title=_unquote(data["title"]),
        nsuid=data["nsuid"],
        product_code=data["productCode"],
    )

    game.slug = slug

    game.description = _itemprop(soup, "description", tag="div")
    game.developer = _itemprop(soup, "manufacturer") or None
    game.publisher = _unquote(data["publisher"]) or None

    rating = data.get("esrbRating")

    if rating:
        game.rating = f"ESRB: {rating}"

    # Genres
    game.genres = list(sorted([
        genre for genre in _unquote(data["genre"]).split(",")
        if genre != "Undefined"
    ]))

    # Languages
    game.languages = _class(soup, "languages")

    if game.languages:
        game.languages = game.languages.split(", ")
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
    except (KeyError, ValueError):
        pass

    # Game size
    rom_size = _itemprop(soup, "romSize")

    if rom_size:
        value, unit = rom_size.split(" ")

        if unit.lower() == "blocks":
            value = int(value) // 8
        else:
            value = round(float(value) * (1024 if unit == "GB" else 1))
    else:
        value = None

    game.megabytes = value

    # Features
    game.amiibo = None  # unsupported
    game.demo = _aria_label(soup, "Download game demo opens in another window.") is not None
    game.dlc = _class(soup, "dlc", tag="section") is not None
    game.iaps = None  # unsupported
    game.free_to_play = data["msrp"] == '0'

    banner_art = soup.find(class_="hero-landscape hero-only")
    game.banner_img = BASE + banner_art.attrs.get("src") if banner_art else None

    if game.platform == N3DS:
        game.street_pass = "StreetPass" in game.description
        game.virtual_console = soup.find("img", attrs={"alt": "Virtual Console"}) is not None

    if game.platform == SWITCH:
        game.local_multiplayer = None  # unsupported
        game.game_vouchers = _aria_label(soup, "Eligible for Game Vouchers") is not None
        game.nso_required = _aria_label(soup, "online-play") is not None
        game.save_data_cloud = _aria_label(soup, "save-data-cloud") is not None

    return game


@validate.nsuid
def game_info(*, nsuid: str) -> Game:
    """
        Given a valid nsuid for the NA region, it will retrieve the
    information of the game with that nsuid from Nintendo of America.

    Game data
    ---------
        * platform: str ["Nintendo 3DS", "Nintendo Switch"]
        * region: str ["NA"]
        * title: str
        * nsuid: str
        * product_code: str

        * slug: str

        * amiibo: bool (unsupported)
        * demo: bool
        * description: str
        * developer: str (optional)
        * dlc: bool
        * free_to_play: bool
        * genres: List[str]
        * iaps: bool (unsupported)
        * languages: List[str]
        * megabytes: int
        * players: int
        * publisher: str (optional)
        * rating: str (ESRB)
        * release_date: datetime

        # 3DS Features
        * street_pass: bool
        * virtual_console: bool

        # Switch Features
        * local_multiplayer: bool (unsupported)
        * game_vouchers: bool
        * nso_required: bool
        * save_data_cloud: bool

        * banner_img: str

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    nintendeals.classes.N3DSGame:
        3DS game from Nintendo of America.
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of America.
    None:
        No game with the provided nsuid was found on Nintendo of America.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid was either none or has an invalid format.
    """
    slug = algolia.find_by_nsuid(nsuid)

    log.info("Fetching info for %s", nsuid)

    if nsuid.startswith("5"):
        return _scrap(N3dsGame, slug=slug)

    if nsuid.startswith("7"):
        return _scrap(SwitchGame, slug=slug)

    return None
