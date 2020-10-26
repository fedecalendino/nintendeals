from typing import Optional

from nintendeals.commons.classes.games import Game
from nintendeals.noe.api import nintendo
from nintendeals.noe.util import build_game


def game_info(nsuid: str) -> Optional[Game]:
    """
    Given a game's `nsuid` for the EU region, it will retrieve its information
    from Nintendo of Europe.

    Available Features
    ------------------
        * Nintendo 3DS
            - AMIIBO
            - DEMO
            - DLC
        * Nintendo WiiU
            - AMIIBO
            - DEMO
            - DLC
        * Nintendo Switch
            - AMIIBO
            - DEMO
            - DLC
            - NSO_REQUIRED
            - SAVE_DATA_CLOUD
            - VOICE_CHAT

    Parameters
    ----------
    nsuid: str
        Valid nsuid of a nintendo game.

    Returns
    -------
    nintendeals.classes.common.Game:
        Information of the game.
    """
    data = nintendo.search_by_nsuid(nsuid)

    return build_game(data) if data else None
