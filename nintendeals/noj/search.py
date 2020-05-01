from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.noj import list_switch_games


def search_switch_games(
        *,
        title: str = None,
        release_date: datetime = None,
        release_date_from: datetime = None,
        release_date_to: datetime = None,
) -> Iterator[Game]:
    for game in list_switch_games():
        if title:
            if title not in game.title:
                continue

        if release_date and game.release_date:
            if release_date != game.release_date:
                continue

        if release_date_from and game.release_date:
            if release_date_from > game.release_date:
                continue

        if release_date_to and game.release_date:
            if release_date_to < game.release_date:
                continue

        yield game
