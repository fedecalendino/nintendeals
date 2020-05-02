import logging
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.helpers import filter_by_date
from nintendeals.noj import list_switch_games

log = logging.getLogger(__name__)


def search_switch_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and fillter all the games in Nintendo of Japan. A subset of data
    will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str = "Nintendo Switch"
        * region: str = "JP"

        * developer: str
        * free_to_play: bool
        * release_date: datetime (may be None)

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
        Iterator of games from Nintendo of Japan.
    """
    log.info("Searching nintendo switch games")

    for game in list_switch_games():
        if title and title not in game.title:
            continue

        if not filter_by_date(
                game.release_date,
                released_at,
                released_after,
                released_before
        ):
            continue

        yield game
