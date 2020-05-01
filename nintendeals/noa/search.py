from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.noa import list_switch_games


def search_switch_games(
        *,
        title: str = None,
        release_date: datetime = None,
        release_date_from: datetime = None,
        release_date_to: datetime = None,
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
    release_date: datetime (Optional)
        Keep only those games that have the exact same release date.
    release_date_from: datetime (Optional)
        Keep only those games have a release date later than this.
    release_date_to: datetime (Optional)
        Keep only those games have a release date prior than this.

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of games from Nintendo of America.
    """
    params = {}

    if title:
        params = {"query": title}

    for game in list_switch_games(**params):
        if release_date:
            if not game.release_date \
                    or release_date != game.release_date:
                continue

        if release_date_from:
            if not game.release_date \
                    or release_date_from > game.release_date:
                continue

        if release_date_to:
            if not game.release_date \
                    or release_date_to < game.release_date:
                continue

        yield game
