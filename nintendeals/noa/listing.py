from typing import Tuple, Iterator
from nintendeals.noa.external.algolia import search_games


def list_games(platform: str) -> Iterator[Tuple[str, str]]:
    yield from search_games(platform=platform)
