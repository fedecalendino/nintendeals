from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.noe import list_switch_games


def search_switch_games(
        *,
        title: str = None,
        release_date: datetime = None,
        release_date_from: datetime = None,
        release_date_to: datetime = None,
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
    release_date: datetime (Optional)
        Keep only those games that have the exact same release date.
    release_date_from: datetime (Optional)
        Keep only those games have a release date later than this.
    release_date_to: datetime (Optional)
        Keep only those games have a release date prior than this.

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Iterator of games from Nintendo of Europe.
    """
    params = {}

    if title:
        params = {"query": f"\"{title}\""}

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
