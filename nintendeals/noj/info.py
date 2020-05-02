import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nintendeals import validate
from nintendeals.classes.games import Game
from nintendeals.constants import JP, PLATFORMS
from nintendeals.exceptions import NsuidMismatch

DETAIL_URL = "https://ec.nintendo.com/JP/jp/titles/{nsuid}"
EXTRA_INFO_URL = "https://search.nintendo.jp/nintendo_soft/search.json"

log = logging.getLogger(__name__)


@validate.nsuid
def _get_extra_info(*, nsuid: str) -> json:
    response = requests.get(EXTRA_INFO_URL, params={"q": nsuid})

    return response.json()["result"]["items"][-1]


def _scrap(url: str) -> Game:
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

    game.amiibo = extra_info.get("amiibo", "0") == "1"
    game.demo = len(data.get("demos", [])) > 0
    game.description = data["description"]
    game.developer = extra_info["maker"]
    game.dlc = data.get("has_aoc", False)
    game.free_to_play = extra_info.get("dprice") == 0.0
    game.game_vouchers = len(data.get("included_pretickets", [])) > 0
    game.iaps = data.get("in_app_purchase", False)
    game.local_multiplayer = data["player_number"].get("local_min", 0) > 0
    game.online_play = "Nintendo Switch Online" in features
    game.publisher = data["publisher"]["name"]
    game.save_data_cloud = data.get("cloud_backup_type") == "supported"

    # Unknown
    game.voice_chat = None

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

        * amiibo: bool
        * demo: bool
        * description: str
        * developer: str
        * dlc: bool
        * free_to_play: bool
        * game_vouchers: bool
        * genres: List[str]
        * iaps: bool
        * languages: List[str]
        * local_multiplayer: bool
        * online_play: bool
        * players: int
        * publisher: str
        * release_date: datetime
        * save_data_cloud: bool
        * size: int

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
    url = DETAIL_URL.format(nsuid=nsuid)

    log.info("Fetching info for %s from %s", nsuid, url)

    return _scrap(url)
