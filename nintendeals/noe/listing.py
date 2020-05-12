import logging
from datetime import datetime
from typing import Iterator, Type, Union

import requests

from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.constants import EU, N3DS, SWITCH

log = logging.getLogger(__name__)


def _list_games(
    game_class: Type,
    system_name: str,
    **kwargs
) -> Iterator[Union[N3dsGame, SwitchGame]]:
    query = kwargs.get("query", "*")
    nsuid = kwargs.get("nsuid")

    if not nsuid:
        fq = f"type:GAME AND system_names_txt:\"{system_name}\""
    else:
        fq = f"type:GAME AND nsuid_txt:\"{nsuid}\""

    rows = 200
    start = -rows

    while True:
        start += rows

        params = {
            "q": query,
            "wt": "json",
            "sort": "title asc",
            "start": start,
            "rows": rows,
            "fq": fq
        }

        response = requests.get(
            url='https://search.nintendo-europe.com/en/select',
            params=params
        )

        if response.status_code != 200:
            break

        json = response.json().get('response').get('docs', [])

        if not len(json):
            break

        for data in json:
            product_codes = [
                pc for pc in data.get("product_code_txt", [])
                if "-" not in pc
            ] or [None]

            nsuids = list(reversed(sorted(data.get("nsuid_txt", [None]))))

            game = game_class(
                region=EU,
                title=data["title_extras_txt"][0],
                nsuid=nsuids[0],
                product_code=product_codes[0],
            )

            game.slug = data.get("url")

            game.developer = data.get("developer")
            game.publisher = data.get("publisher")
            game.genres = data.get("pretty_game_categories_txt", [])
            game.players = data.get("players_to")
            game.languages = list(map(
                lambda lang: lang.title(),
                data.get("language_availability", [])
            ))

            try:
                game.release_date = datetime.strptime(
                    data["dates_released_dts"][0].split("T")[0],
                    '%Y-%m-%d'
                )
            except (ValueError, TypeError):
                game.release_date = None

            if "datasize_readable_txt" in data:
                size, unit = data.get("datasize_readable_txt", [""])[0].split()

                if unit.lower() == "blocks":
                    game.size = int(size) // 8

            # Features
            game.amiibo = data.get("near_field_comm_b", False)
            game.demo = data.get("demo_availability", False)
            game.dlc = data.get("dlc_shown_b", False)
            game.free_to_play = data.get("price_regular_f") == 0.0

            if game.platform == N3DS:
                game.download_play = data.get("download_play", False)
                game.motion_control = data.get("motion_control_3ds", False)
                game.spot_pass = data.get("spot_pass", False)
                game.street_pass = data.get("street_pass", False)
                game.virtual_console = '3ds_virtualconsole' in data.get("system_type", [""])[0]

            if game.platform == SWITCH:
                game.local_multiplayer = data.get("local_play", False)
                game.nso_required = data.get("paid_subscription_required_b", False)
                game.save_data_cloud = data.get("cloud_saves_b", False)
                game.game_vouchers = data.get("switch_game_voucher_b", False)
                game.voice_chat = data.get("voice_chat_b", False)

            yield game


def list_3ds_games(**kwargs) -> Iterator[N3dsGame]:
    """
        List all the 3DS games in Nintendo of Europe. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (may be None)
        * region: str = "EU"
        * platform: str = "Nintendo 3DS"

        * developer: str
        * genres: List[str]
        * languages: List[str]
        * players: int
        * publisher: str
        * release_date: datetime

        # Features
        * amiibo: bool
        * demo: bool
        * dlc: bool
        * free_to_play: bool

        # 3DS Features
        * download_play: bool
        * motion_control: bool
        * spot_pass: bool
        * street_pass: bool
        * virtual_console: bool

    Yields
    -------
    nintendeals.classes.N3dsGame:
        3DS game from Nintendo of Europe.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(
        game_class=N3dsGame,
        system_name="3ds",
        **kwargs
    )


def list_switch_games(**kwargs) -> Iterator[SwitchGame]:
    """
        List all the Switch games in Nintendo of Europe. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (may be None)
        * region: str = "EU"
        * platform: str = "Nintendo Switch"

        * developer: str
        * genres: List[str]
        * languages: List[str]
        * players: int
        * publisher: str
        * release_date: datetime

        # Features
        * amiibo: bool
        * demo: bool
        * dlc: bool
        * free_to_play: bool

        # Switch Features
        * game_vouchers: bool
        * local_multiplayer: bool
        * nso_required: bool
        * save_data_cloud: bool
        * voice_chat: bool

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of Europe.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(
        game_class=SwitchGame,
        system_name="Switch",
        **kwargs
    )
