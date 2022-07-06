from typing import Iterator

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Platforms
from nintendeals.noa.api import algolia
from nintendeals.noa.util import build_game


def search_games(query: str, platform: Platforms) -> Iterator[Game]:
    for data in algolia.search_by_query(query, platform):
        yield build_game(data)


def search_switch_games(query: str) -> Iterator[Game]:
    """
    Search for Nintendo Switch games in the NA region.

    Note: game.product_code is unavailable with this method, to get it use the
    method noa.game_info(nsuid).

    Available Features
    ------------------
        * DEMO
        * DLC
        * NSO_REQUIRED

    Parameters
    ----------
    query: str
        Text to search.

    Yields
    -------
    nintendeals.classes.common.Game:
        Information of a game.
    """

    yield from search_games(query, Platforms.NINTENDO_SWITCH)
