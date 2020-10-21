from typing import Optional

from nintendeals.commons.classes.games import Game
from nintendeals.noj.api import nintendo
from nintendeals.noj.util import build_game


def game_info(nsuid: str) -> Optional[Game]:
    data = nintendo.search_by_nsuid(nsuid)

    return build_game(data) if data else None
