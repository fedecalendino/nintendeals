import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes.games import Game
from nintendeals.constants import JP, PLATFORMS
from nintendeals.exceptions import NsuidMismatch

SWITCH_DETAIL_URL = "https://ec.nintendo.com/JP/jp/titles/{nsuid}"
N3DS_DETAIL_URL = "https://www.nintendo.co.jp/titles/{nsuid}"
EXTRA_INFO_URL = "https://search.nintendo.jp/nintendo_soft/search.json"

log = logging.getLogger(__name__)


@validate.nsuid
def _get_extra_info(*, nsuid: str) -> json:
    response = requests.get(EXTRA_INFO_URL, params={"q": nsuid})

    return response.json()["result"]["items"][-1]


def _scrap_3ds(nsuid: str) -> Game:
    extra_info = _get_extra_info(nsuid=nsuid)

    product_code = f"{extra_info['hard'].replace('2_', '')}{extra_info['icode']}"

    game = Game(
        nsuid=nsuid,
        product_code=product_code,
        title=extra_info["title"],
        region=JP,
        platform=PLATFORMS[extra_info['hard']],
    )

    game.developer = extra_info.get("maker")
    game.description = extra_info.get("text")

    # Genres
    game.genres = list(sorted(extra_info.get("genre", [])))

    # Players
    try:
        game.players = max([int(p) for p in extra_info.get("player", [])])
    except ValueError:
        game.players = 0

    # Release date
    try:
        release_date = extra_info["sdate"]
        game.release_date = datetime.strptime(release_date, '%Y.%m.%d')
    except ValueError:
        pass

    # Common Features
    game.amiibo = extra_info.get("amiibo", "0") == "1"
    game.free_to_play = extra_info.get("dprice") == 0.0

    return game


def _scrap_switch(url: str) -> Game:
    response = requests.get(url, allow_redirects=True)
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

    nsuid = str(data["id"])
    extra_info = _get_extra_info(nsuid=nsuid)

    if extra_info["nsuid"] != nsuid:
        raise NsuidMismatch((nsuid, extra_info["nsuid"]))

    platform = data["platform"]["name"]
    product_code = f"{extra_info['hard'].replace('1_', '')}{extra_info['icode']}"

    game = Game(
        nsuid=nsuid,
        product_code=product_code,
        title=data["formal_name"],
        region=JP,
        platform=PLATFORMS[platform],
    )

    game.developer = extra_info["maker"]
    game.description = data["description"]
    game.publisher = data["publisher"]["name"]

    # Genres
    game.genres = list(sorted(data.get("genre", "").split(" / ")))

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
        release_date = data["release_date_on_eshop"]
        game.release_date = datetime.strptime(release_date, '%Y-%m-%d')
    except ValueError:
        pass

    # Game size (in MBs)
    game.size = round(data.get("total_rom_size", 0) / 1024 / 1024)

    # Other properties
    features = list(map(
        lambda lang: lang["name"], data.get("features", [])
    ))

    # Common Features
    game.amiibo = extra_info.get("amiibo", "0") == "1"
    game.demo = len(data.get("demos", [])) > 0
    game.dlc = data.get("has_aoc", False)
    game.free_to_play = extra_info.get("dprice") == 0.0
    game.iaps = data.get("in_app_purchase", False)
    game.local_multiplayer = data["player_number"].get("local_min", 0) > 0
    game.online_play = "Nintendo Switch Online" in features

    # Switch Features
    game.game_vouchers = len(data.get("included_pretickets", [])) > 0
    game.save_data_cloud = data.get("cloud_backup_type") == "supported"

    return game


@validate.nsuid
def game_info(*, nsuid: str) -> Game:
    """
        Given an `nsuid` valid for the Japan region, it will provide the
    complete information of the game with that nsuid provided by Nintendo
    of Japan.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str
        * region: str = "JP"

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
        * iaps: bool
        * local_multiplayer: bool
        * online_play: bool

        # Switch Features
        * save_data_cloud: bool

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    classes.nintendeals.games.Game:
        Information provided by NoJ of the game with the given nsuid.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The nsuid was either none or has an invalid format.
    """
    if nsuid[0] == "7":
        url = SWITCH_DETAIL_URL.format(nsuid=nsuid)
        log.info("Fetching info for %s from %s", nsuid, url)
        return _scrap_switch(url)

    log.info("Fetching info for %s", nsuid)
    return _scrap_3ds(nsuid=nsuid)
