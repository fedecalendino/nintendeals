import re
from datetime import datetime
from typing import Iterator

from nintendeals.classes.games import Game
from nintendeals.constants import NA
from nintendeals.noa.external.algolia import search_games


def list_games(platform: str) -> Iterator[Game]:
    """
        Given a supported platform it will provide an iterator
    of with a subset of data for all games found in the listing
    service Nintendo of America.

    Game data
    ---------
        * title: str
        * region: str (NA)
        * platform: str
        * nsuid: str (optional)

        * description: str
        * free_to_play: bool
        * genres: List[str]
        * na_slug: str
        * players: int
        * publisher: str
        * release_date : datetime

    Parameters
    ----------
    platform: str
        Valid nintendo platform.

    Returns
    -------
    Iterator[classes.nintendeals.games.Game]:
        Partial information of a game provided by NoA.
    """
    for data in search_games(platform=platform):
        game = Game(
            title=data["title"],
            region=NA,
            platform=platform,
            nsuid=data.get("nsuid"),
        )

        game.na_slug = data["slug"]
        game.genres = data.get("categories", [])

        try:
            release_date = data["releaseDateMask"].split("T")[0]
            game.release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            pass

        try:
            game.players = int(re.sub(r"[^\d]*", "", data["players"]))
        except ValueError:
            game.players = 0

        game.description = data.get("description")
        game.free_to_play = data.get("msrp") == 0.0
        game.publisher = data.get("publishers", [None])[0]

        yield game
