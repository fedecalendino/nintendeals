import logging
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.helpers import filter_by_date
from nintendeals.noa import list_switch_games

log = logging.getLogger(__name__)


def search_switch_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and fillter all the games in Nintendo of America. A subset of data
    will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo Switch"
        * region: str = "NA"

        * description: str
        * free_to_play: bool
        * genres: List[str]
        * na_slug: str
        * players: int
        * publisher: str
        * release_date : datetime

    Parameters
    ----------
    title: str (Optional)
        String that should be contained in the title of each game.
    released_at: datetime (Optional)
        Keep only those games that have been released on this date.
    released_after: datetime (Optional)
        Keep only those games that have been released after this date.
    released_before: datetime (Optional)
        Keep only those games that have been released before this date.

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of games from Nintendo of America.
    """
    log.info("Searching nintendo switch games")

    params = {}

    if title:
        params = {"query": title}

    for game in list_switch_games(**params):
        if not filter_by_date(
                game.release_date,
                released_at,
                released_after,
                released_before
        ):
            continue

        yield game
