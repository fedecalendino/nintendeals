import logging
import re
from datetime import datetime
from typing import Iterator, Type, Union

from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.classes.games import Game
from nintendeals.constants import NA
from nintendeals.noa.external import algolia

log = logging.getLogger(__name__)


def _list_games(
    game_class: Type,
    **kwargs
) -> Iterator[Union[N3dsGame, SwitchGame]]:

    for data in algolia.search_games(platform=game_class.platform, **kwargs):
        game = game_class(
            region=NA,
            title=data["title"],
            nsuid=data.get("nsuid"),
        )

        game.slug = data["slug"]
        game.genres = list(sorted(data.get("categories", [])))

        try:
            release_date = data["releaseDateMask"].split("T")[0]
            game.release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            pass

        try:
            game.players = int(re.sub(r"[^\d]*", "", data["players"]))
        except ValueError:
            game.players = 0

        game.description = data.get("description")
        game.free_to_play = data.get("msrp") == 0.0
        game.publisher = data.get("publishers", [None])[0]
        game.developer = data.get("developers", [None])[0]

        game.virtual_console = True if data.get("virtualConsole", "na") != "na" else None

        yield game


def list_3ds_games(**kwargs) -> Iterator[Game]:
    """
        List all the 3DS games in Nintendo of America. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo 3DS"
        * region: str = "NA"
        * slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Features
        * free_to_play: bool

        # 3DS Features
        * virtual_console: bool

    Yields
    -------
    nintendeals.classes.N3dsGame:
        3DS game from Nintendo of America.
    """
    log.info("Fetching list of Nintendo 3DS games")

    yield from _list_games(N3dsGame, **kwargs)


def list_switch_games(**kwargs) -> Iterator[SwitchGame]:
    """
        List all the Switch games in Nintendo of America. The following subset
    of data will be available for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo Switch"
        * region: str = "NA"
        * slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Common Features
        * free_to_play: bool

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of America.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SwitchGame, **kwargs)
