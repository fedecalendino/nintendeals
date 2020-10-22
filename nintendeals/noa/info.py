from typing import Optional

from nintendeals.commons.classes.games import Game
from nintendeals.noa.api import algolia
from nintendeals.noa.scrapers import nintendo
from nintendeals.noa.util import build_game


def game_info_by_nsuid(nsuid: str) -> Optional[Game]:
    data = algolia.search_by_nsuid(nsuid)

    if not data:
        return None

    data["extra"] = nintendo.scrap(data["slug"])

    return build_game(data)


def game_info_by_slug(slug: str) -> Optional[Game]:
    extra = nintendo.scrap(slug)
    nsuid = extra.get("nsuid")

    if not nsuid:
        return None

    data = algolia.search_by_nsuid(nsuid)

    if not data:
        return None

    data["extra"] = extra

    return build_game(data)


def game_info(nsuid: str = None, slug: str = None) -> Optional[Game]:
    if nsuid:
        return game_info_by_nsuid(nsuid)

    if slug:
        return game_info_by_slug(slug)

    return None
