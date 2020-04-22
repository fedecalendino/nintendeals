from typing import Tuple, Iterator
from string import ascii_lowercase, digits
from nintendeals.constants import SWITCH
from nintendeals.noa.external.algolia import search_games


SYSTEM_NAMES = {
    SWITCH: "Switch",
}


def list_games(platform: str) -> Iterator[Tuple[str, str]]:
    assert platform in SYSTEM_NAMES

    uniques = {}

    # Algolia limits 1000 results per query, this allows to fetch
    # all games by doing multiple queries with different characters
    for character in ascii_lowercase + digits:
        games = list(search_games(platform=platform, query=character))
        print(character, len(games))
        uniques.update(games)

    yield from uniques.items()
