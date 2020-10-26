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
    """
    Given a game's `nsuid` or url `slug` for the NA region, it will retrieve
    its information from Nintendo of America.

    Available Features
    ------------------
        * Nintendo 3DS
            - DEMO
        * Nintendo WiiU
            - DEMO.
        * Nintendo Switch
            - DEMO
            - DLC
            - NSO_REQUIRED
            - SAVE_DATA_CLOUD

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.
    slug: str
        Valid slug from NA's eShop.

    Returns
    -------
    nintendeals.classes.common.Game:
        Information of the game.
    """
    if nsuid:
        return game_info_by_nsuid(nsuid)

    if slug:
        return game_info_by_slug(slug)

    return None
