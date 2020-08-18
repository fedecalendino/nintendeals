import logging
import re
from datetime import datetime
from typing import Iterator, Type, Union

from nintendeals.classes import N3dsGame, SwitchGame
from nintendeals.classes.games import Game
from nintendeals.constants import NA, N3DS
from nintendeals.noa.external import algolia

BASE = "https://www.nintendo.com"

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
        game.genres = list(sorted(data.get("genres", [])))

        try:
            release_date = data["releaseDateDisplay"].split("T")[0]
            game.release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            pass

        try:
            game.players = int(re.sub(r"[^\d]*", "", data["numOfPlayers"]))
        except ValueError:
            game.players = 0

        game.description = data.get("description")
        game.free_to_play = data.get("msrp") == 0.0
        game.publisher = (data.get("publishers") or [None])[0]
        game.developer = (data.get("developers") or [None])[0]

        rating = data.get("esrbRating")

        if rating:
            game.rating = f"ESRB: {rating}"

        box_art = data.get("boxArt")
        game.cover_img = (BASE + box_art) if box_art else None

        if game.platform == N3DS:
            game.virtual_console = data.get("virtualConsole", "na") != "na"

        yield game


def list_3ds_games(**kwargs) -> Iterator[Game]:
    """
        List all the 3DS games in Nintendo of America. The following subset
    of data will be available for each game.

    Game data
    ---------
        * platform: str ["Nintendo 3DS"]
        * region: str ["NA"]
        * title: str
        * nsuid: str (optional)
        * product_code: str (unsupported)

        * slug: str

        * description: str
        * developer: str
        * free_to_play: bool
        * genres: List[str]
        * publisher: str
        * rating: str (ESRB)
        * release_date: datetime
        * virtual_console: bool

        * cover_img: str

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
        * platform: str ["Nintendo Switch"]
        * region: str ["NA"]
        * title: str
        * nsuid: str (optional)
        * product_code: str (unsupported)

        * slug: str

        * description: str
        * developer: str
        * free_to_play: bool
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        * box_art: str

    Yields
    -------
    nintendeals.classes.SwitchGame:
        Switch game from Nintendo of America.
    """
    log.info("Fetching list of Nintendo Switch games")

    yield from _list_games(SwitchGame, **kwargs)
