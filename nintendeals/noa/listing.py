from typing import Iterator

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Platforms
from nintendeals.noa.api import algolia
from nintendeals.noa.util import build_game


def list_games(platform: Platforms) -> Iterator[Game]:
    for data in algolia.search_by_platform(platform):
        yield build_game(data)


def list_switch_games() -> Iterator[Game]:
    yield from list_games(Platforms.NINTENDO_SWITCH)
