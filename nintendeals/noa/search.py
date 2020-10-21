from typing import Iterator

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Platforms
from nintendeals.noa.api import algolia
from nintendeals.noa.util import build_game


def search_games(query: str, platform: Platforms) -> Iterator[Game]:
    for data in algolia.search_by_query(query, platform):
        yield build_game(data)


def search_switch_games(query: str) -> Iterator[Game]:
    yield from search_games(query, Platforms.NINTENDO_SWITCH)
