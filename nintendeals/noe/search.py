from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.noe import list_switch_games


def search_switch_games(
        *,
        title: str = None,
        release_date: datetime = None,
        release_date_from: datetime = None,
        release_date_to: datetime = None,
) -> Iterator[Game]:
    params = {}

    if title:
        params = {"query": f"\"{title}\""}

    for game in list_switch_games(**params):
        if release_date:
            if not game.release_date \
                    or release_date != game.release_date:
                continue

        if release_date_from:
            if not game.release_date \
                    or release_date_from > game.release_date:
                continue

        if release_date_to:
            if not game.release_date \
                    or release_date_to < game.release_date:
                continue

        yield game
