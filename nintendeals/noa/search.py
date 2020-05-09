import logging
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.helpers import filter_by_date
from nintendeals.noa import list_3ds_games, list_switch_games

log = logging.getLogger(__name__)


def _search_games(
    listing,
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    params = {}

    if title:
        params = {"query": title}

    for game in listing(**params):
        if not filter_by_date(
                game.release_date,
                released_at,
                released_after,
                released_before
        ):
            continue

        yield game


def search_switch_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and filter all the Switch games in Nintendo of America. The
    following subset of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo Switch"
        * region: str = "NA"
        * na_slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Common Features
        * free_to_play: bool

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
        Iterator of Switch games from Nintendo of America.
    """
    log.info("Searching Nintendo Switch games")

    yield from _search_games(
        list_switch_games,
        title=title,
        released_at=released_at,
        released_after=released_after,
        released_before=released_before,
    )


def search_3ds_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and fillter all the 3DS games in Nintendo of America. The
    following subset of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (Unavailable)
        * platform: str = "Nintendo 3DS"
        * region: str = "NA"
        * na_slug: str

        * description: str
        * developer: str
        * genres: List[str]
        * publisher: str
        * release_date: datetime

        # Common Features
        * free_to_play: bool

        # 3DS Features
        * virtual_console: bool

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
        Iterator of 3DS games from Nintendo of America.
    """
    log.info("Searching Nintendo 3DS games")

    yield from _search_games(
        list_3ds_games,
        title=title,
        released_at=released_at,
        released_after=released_after,
        released_before=released_before,
    )
