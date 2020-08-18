import json
import logging
from datetime import datetime
from typing import Union, Type

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.constants import JP

log = logging.getLogger(__name__)

RATINGS = {
    "0": None,
    "1": "A",
    "2": "B",
    "3": "C",
    "4": "D",
    "5": "Z",
}


def _get_extra_info(*, nsuid: str) -> json:
    response = requests.get(
        url="https://search.nintendo.jp/nintendo_soft/search.json",
        params={"q": nsuid}
    )

    if response.status_code != 200:
        return None

    items = response.json()["result"]["items"]

    if not items:
        return None

    return items[-1]


def _scrap_3ds(nsuid: str) -> N3dsGame:
    extra = _get_extra_info(nsuid=nsuid)

    if not extra:
        return None

    product_code = f"{extra['hard'][2:]}{extra['icode']}"

    game = N3dsGame(
        title=extra["title"],
        region=JP,
        nsuid=nsuid,
        product_code=product_code,
    )

    game.developer = extra.get("maker")
    game.description = extra.get("text")

    rating = RATINGS.get(extra.get("cero", ["0"])[0])

    if rating:
        game.rating = f"CERO: {rating}"

    # Genres
    game.genres = list(sorted(extra.get("genre", [])))

    # Players
    try:
        game.players = max((
            int(p) for p in extra.get("player", [])
        ))
    except ValueError:
        game.players = 0

    # Release date
    try:
        game.release_date = datetime.strptime(
            extra["sdate"],
            '%Y.%m.%d'
        )
    except ValueError:
        pass

    # Features
    game.amiibo = extra.get("amiibo", "0") == "1"
    game.free_to_play = extra.get("dprice") == 0.0

    return game


def _scrap_switch(nsuid: str) -> SwitchGame:
    extra = _get_extra_info(nsuid=nsuid)

    if not extra:
        return None

    url = f"https://ec.nintendo.com/JP/jp/titles/{nsuid}"
    response = requests.get(url, allow_redirects=True)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, features="html.parser")

    script = next((
        s for s in soup.find_all("script")
        if "var NXSTORE = NXSTORE || {};" in str(s)
    ))

    json_data = next((
        line for line in str(script).split("\n")
        if "NXSTORE.titleDetail.jsonData = " in line
    ))

    data = json.loads(
        json_data.replace("NXSTORE.titleDetail.jsonData = ", "")[:-1]
    )

    product_code = f"{extra['hard'][2:]}{extra['icode']}"

    game = SwitchGame(
        region=JP,
        title=data["formal_name"],
        nsuid=nsuid,
        product_code=product_code,
    )

    game.developer = extra["maker"]
    game.description = data["description"]
    game.publisher = data["publisher"]["name"]

    rating = data.get("rating_info")

    if rating:
        rating = rating["rating"]["name"]
        game.rating = f"CERO: {rating}"

    # Genres
    game.genres = list(sorted(
        data.get("genre", "").split(" / ")
    ))

    # Languages
    game.languages = list(sorted(map(
        lambda lang: lang["name"], data.get("languages", [])
    )))

    # Players
    try:
        game.players = max(data.get("player_number", {}).values())
    except ValueError:
        game.players = 0

    # Release date
    try:
        game.release_date = datetime.strptime(
            data.get("release_date_on_eshop", ""),
            '%Y-%m-%d'
        )
    except ValueError:
        pass

    # Game size (in MBs)
    game.megabytes = round(data.get("total_rom_size", 0) / 1024 / 1024)

    # Other properties
    features = list(map(
        lambda feature: feature["name"], data.get("features", [])
    ))

    game.banner_img = data.get("hero_banner_url")

    # Features
    game.amiibo = extra.get("amiibo", "0") == "1"
    game.demo = len(data.get("demos", [])) > 0
    game.dlc = data.get("has_aoc", False)
    game.free_to_play = extra.get("dprice") == 0.0
    game.iaps = data.get("in_app_purchase", False)

    game.game_vouchers = len(data.get("included_pretickets", [])) > 0
    game.local_multiplayer = data["player_number"].get("local_min", 0) > 0
    game.nso_required = "Nintendo Switch Online" in features
    game.save_data_cloud = data.get("cloud_backup_type") == "supported"

    return game


@validate.nsuid
def game_info(*, nsuid: str) -> Union[N3dsGame, SwitchGame, Type[None]]:
    """
        Given a valid nsuid for the JP region, it will retrieve the
    information of the game with that nsuid from Nintendo of Japan.

    Game data
    ---------
        * platform: str ["Nintendo 3DS", "Nintendo Switch"]
        * region: str ["JP"]
        * title: str
        * nsuid: str
        * product_code: str

        * demo: bool
        * description: str
        * developer: str
        * dlc: bool
        * free_to_play: bool
        * genres: List[str]
        * iaps: bool
        * languages: List[str]
        * local_multiplayer: bool
        * megabytes: int
        * publisher: str
        * rating: str (CERO)
        * release_date: datetime

        * banner_img: str

        # Switch Features
        * save_data_cloud: bool
        * nso_required: bool

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    nintendeals.classes.N3DSGame:
        3DS game from Nintendo of Japan.
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Japan.
    None:
        No game with the provided nsuid was found on Nintendo of Japan.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid was either none or has an invalid format.
    """
    if nsuid.startswith("5"):
        log.info("Fetching info for %s", nsuid)
        return _scrap_3ds(nsuid=nsuid)

    if nsuid.startswith("7"):
        log.info("Fetching info for %s", nsuid)
        return _scrap_switch(nsuid=nsuid)

    return None
