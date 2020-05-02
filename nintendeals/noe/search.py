import logging
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.helpers import filter_by_date
from nintendeals.noe import list_switch_games

log = logging.getLogger(__name__)


def search_switch_games(
    *,
    title: str = None,
    released_at: datetime = None,
    released_after: datetime = None,
    released_before: datetime = None,
) -> Iterator[Game]:
    """
        Search and fillter all the games in Nintendo of Europe. A subset of data
    will be provided for each game.

    Game data
    ---------
        * title: str
        * nsuid: str (may be None)
        * product_code: str (may be None)
        * region: str = "EU"
        * platform: str = "Nintendo Switch"

        * amiibo: bool
        * demo: bool
        * developer: str
        * dlc: bool
        * free_to_play: bool
        * game_vouchers: bool
        * genres: List[str]
        * languages: List[str]
        * local_multiplayer: bool
        * online_play: bool
        * players: int
        * publisher: str
        * release_date: datetime
        * save_data_cloud: bool
        * voice_chat: bool

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
        Iterator of games from Nintendo of Europe.
    """
    log.info("Searching nintendo switch games")

    params = {}

    if title:
        params = {"query": f"\"{title}\""}

    for game in list_switch_games(**params):
        if not filter_by_date(
                game.release_date,
                released_at,
                released_after,
                released_before
        ):
            continue

        yield game
