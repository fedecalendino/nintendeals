from typing import Iterator

from nintendeals.commons.classes.games import Game
from nintendeals.commons.enumerates import Platforms
from nintendeals.noe.api import nintendo
from nintendeals.noe.util import build_game


def list_games(platform: Platforms) -> Iterator[Game]:
    for data in nintendo.search_by_platform(platform):
        yield build_game(data)


def list_3ds_games() -> Iterator[Game]:
    yield from list_games(Platforms.NINTENDO_3DS)


def list_switch_games() -> Iterator[Game]:
    yield from list_games(Platforms.NINTENDO_SWITCH)


def list_wiiu_games() -> Iterator[Game]:
    yield from list_games(Platforms.NINTENDO_WIIU)
