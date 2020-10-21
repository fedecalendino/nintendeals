from typing import Optional

from nintendeals.commons.classes.games import Game
from nintendeals.noa.api import algolia
from nintendeals.noa.scrapers import nintendo
from nintendeals.noa.util import build_game


def game_info(nsuid: str) -> Optional[Game]:
    data = algolia.search_by_nsuid(nsuid)

    if not data:
        return None

    data["extra"] = nintendo.scrap(data["slug"])

    return build_game(data)
