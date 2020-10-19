import logging
import re
from datetime import datetime
from typing import Iterator, Type

from nintendeals.classes import SwitchGame
from nintendeals.constants import NA
from nintendeals.noa.api import algolia

BASE = "https://www.nintendo.com"

log = logging.getLogger(__name__)


def _list_games(
    game_class: Type,
    **kwargs
) -> Iterator[SwitchGame]:

    for data in algolia.list_games(platform=game_class.platform):
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
        except (KeyError, ValueError):
            pass

        try:
            game.players = int(re.sub(r"[^\d]*", "", data["numOfPlayers"]))
        except (KeyError, ValueError):
            game.players = None

        game.description = data.get("description")
        game.free_to_play = data.get("msrp") == 0.0
        game.publisher = (data.get("publishers") or [None])[0]
        game.developer = (data.get("developers") or [None])[0]

        rating = data.get("esrbRating")

        if rating:
            game.rating = f"ESRB: {rating}"

        box_art = data.get("boxArt")
        game.cover_img = (BASE + box_art) if box_art else None

        yield game


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
        * players: int (optional)
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
