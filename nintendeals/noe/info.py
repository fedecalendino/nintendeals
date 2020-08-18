import logging
from datetime import datetime
from typing import Type, Union

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.classes.games import Game
from nintendeals.constants import EU
from nintendeals.noe.listing import list_3ds_games

log = logging.getLogger(__name__)


def _sibling(soup: BeautifulSoup, string: str, tag: str = "p") -> str:
    p = soup.find(tag, class_="game_info_title", string=string)

    if not p:
        return None

    sib = p.find_next_sibling("p")

    if not sib:
        return None

    return sib.text


def _scrap_switch(nsuid: str) -> Game:
    url = f"https://ec.nintendo.com/GB/en/titles/{nsuid}"
    response = requests.get(url, allow_redirects=True)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, features="html.parser")

    scripts = list(filter(
        lambda s: "var nsuids = [" in str(s), soup.find_all('script')
    ))

    if not scripts:
        return None

    script = scripts[0]
    lines = [
        line.strip().replace("\",", "") for line in str(script).split("\n")
        if ':' in line
    ]

    data = {}

    for line in lines:
        split = line.split(": \"")

        if len(split) != 2:
            continue

        data[split[0].replace("\"", "")] = split[1].replace("\"", "")

    game = SwitchGame(
        region=EU,
        title=soup.find("h1").text,
        nsuid=data["nsuid"],
        product_code=data["productCode"],
    )

    game.slug = response.url.replace("https://www.nintendo.co.uk", "")

    game.description = soup.find("div", class_="col-xs-12 content").text.strip()
    game.developer = _sibling(soup, "Developer")
    game.publisher = _sibling(soup, "Publisher")

    rating = soup.find("div", class_="age-rating")

    if rating:
        game.rating = f"PEGI: {rating.text.strip()}"

    # Genres
    game.genres = list(sorted(map(
        lambda g: g.strip(), _sibling(soup, string="Categories").split(",")
    )))

    # Languages
    game.languages = list(sorted(
        _sibling(soup, string="Languages").split(", ")
    ))

    # Players
    try:
        text = _sibling(soup, "Players")
        game.players = max(map(int, text.split(" - ")))
    except (AttributeError, ValueError):
        game.players = 0

    # Release date
    try:
        release_date = data["releaseDate"]
        game.release_date = datetime.strptime(release_date, '%d/%m/%Y')
    except ValueError:
        pass

    # Game size (in MBs)
    rom_size = _sibling(soup, "Download size")
    if rom_size:
        value, unit = rom_size.split(" ")
        value = round(float(value))
    else:
        value = None

    game.megabytes = value

    overlay_art = soup.find("vc-price-box-overlay").attrs.get(":purchase-img-src")
    game.banner_img = "https:" + overlay_art.replace("'", "")

    packshot_art = soup.find("vc-price-box-standard").attrs.get(":packshot-src")
    game.cover_img = "https:" + packshot_art.replace("'", "")

    # Other properties
    features = _sibling(soup, string="Features")

    # Common Features
    game.amiibo = "amiibo" in features
    game.demo = "Demo available" in features
    game.dlc = "Downloadable content" in features
    game.free_to_play = "\"offdeviceProductPrice\": \"0.0\"" in response.text
    game.iaps = "Offers in-game purchases" in response.text

    # Switch Features
    game.local_multiplayer = "Local multiplayer" in features
    game.game_vouchers = None  # unsupported
    game.nso_required = "Paid online membership service" in features
    game.save_data_cloud = "Save Data Cloud" in features
    game.voice_chat = "Voice Chat" in features

    return game


@validate.nsuid
def game_info(*, nsuid: str) -> Union[N3dsGame, SwitchGame, Type[None]]:
    """
        Given a valid nsuid for the EU region, it will retrieve the
    information of the game with that nsuid from Nintendo of Europe.

    Game data
    ---------
        * platform: str ["Nintendo 3DS", "Nintendo Switch"]
        * region: str ["EU"]
        * title: str
        * nsuid: str (optional)
        * product_code: str (optional)

        * slug: str

        * amiibo: bool
        * demo: bool
        * description: str
        * developer: str (optional)
        * dlc: bool
        * free_to_play: bool
        * genres: List[str]
        * iaps: bool
        * languages: List[str]
        * megabytes: int
        * players: int
        * publisher: str
        * rating: str (PEGI)
        * release_date: datetime

        * banner_img: str
        * cover_img: str

        # Switch Features
        * local_multiplayer: bool
        * game_vouchers: bool (unsupported)
        * nso_required: bool
        * save_data_cloud: bool
        * voice_chat: bool

        # 3DS Features
        * download_play: bool
        * motion_control: bool
        * spot_pass: bool
        * street_pass: bool
        * virtual_console: bool

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    nintendeals.classes.N3DSGame:
        3DS game from Nintendo of Europe.
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Europe.
    None:
        No game with the provided nsuid was found on Nintendo of Europe.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid was either none or has an invalid format.
    """
    if nsuid.startswith("5"):
        log.info("Fetching info for %s", nsuid)
        games = list(list_3ds_games(nsuid=nsuid))
        return games[0] if games else None

    if nsuid.startswith("7"):
        log.info("Fetching info for %s", nsuid)
        return _scrap_switch(nsuid=nsuid)

    return None
