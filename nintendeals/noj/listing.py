from typing import Iterator

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Platforms
from nintendeals.noj.api import nintendo
from nintendeals.noj.util import build_game


def list_games(platform: Platforms) -> Iterator[Game]:
    for data in nintendo.search_by_platform(platform):
        yield build_game(data)


def list_switch_games() -> Iterator[Game]:
    """
    Get a list of Nintendo WiiU games for the JP region.

    Available Features
    ------------------
        * AMIIBO
        * DLC
        * NSO_REQUIRED

    Yields
    -------
    nintendeals.classes.common.Game:
        Information of a game.
    """

    yield from list_games(Platforms.NINTENDO_SWITCH)
