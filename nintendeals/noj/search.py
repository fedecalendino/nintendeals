import logging
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.helpers import filter_by_date
from nintendeals.noj import list_3ds_games, list_switch_games

log = logging.getLogger(__name__)


def _search_games(
    listing,
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    for game in listing():
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


def search_3ds_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and filter all the 3DS games in Nintendo of Japan. The
    following subset of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str = "Nintendo 3DS"
        * region: str = "JP"

        * developer: str
        * release_date: datetime (may be None)

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
        Iterator of 3DS games from Nintendo of Europe.
    """
    log.info("Searching Nintendo 3DS games")

    yield from _search_games(
        list_3ds_games,
        title=title,
        released_at=released_at,
        released_after=released_after,
        released_before=released_before,
    )


def search_switch_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and filter all the Switch games in Nintendo of Japan. The
    following subset of data will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str
        * product_code: str
        * platform: str = "Nintendo Switch"
        * region: str = "JP"

        * developer: str
        * release_date: datetime (may be None)

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
        Iterator of Switch games from Nintendo of Europe.
    """
    log.info("Searching Nintendo Switch games")

    yield from _search_games(
        list_switch_games,
        title=title,
        released_at=released_at,
        released_after=released_after,
        released_before=released_before,
    )
