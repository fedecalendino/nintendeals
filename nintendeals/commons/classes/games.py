from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from nintendeals.api.prices import get_price
from nintendeals.commons.classes.prices import Price
from nintendeals.commons.enumerates import (
    Features,
    Platforms,
    Ratings,
    Regions,
)


class Game:

    def __init__(
        self,
        platform: Platforms,
        region: Regions,
        title: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        self.platform: Platforms = platform
        self.region: Regions = region
        self.title: str = title
        self.nsuid: str = nsuid
        self.product_code: str = product_code

        self.description: str = None
        self.slug: str = None

        self.players: int = 0

        self.free_to_play: bool = False

        self.release_date: datetime = None

        self.developers: List[str] = []
        self.categories: List[str] = []
        self.languages: List[str] = []
        self.publishers: List[str] = []

        self.rating: Tuple[Ratings, Any] = (None, None)

        self.features: Dict[Features, Any] = {}

    @property
    def unique_id(self) -> Optional[str]:
        if not self.product_code:
            return None

        return self.product_code[-5:-1]

    def price(self, country: str) -> Price:
        return get_price(country=country, game=self)

    def url(self, country: str, lang: str = "en") -> Optional[str]:
        if not self.nsuid:
            return None

        return f"https://ec.nintendo.com/{country}/{lang}/titles/{self.nsuid}"

    def __repr__(self):
        return self.title
