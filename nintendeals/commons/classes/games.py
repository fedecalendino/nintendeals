from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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

        self.description: Optional[str] = None
        self.slug: Optional[str] = None

        self.players: int = 0

        self.free_to_play: Optional[bool] = None

        self.release_date: Optional[datetime] = None

        self.categories: List[str] = []
        self.developers: List[str] = []
        self.languages: List[str] = []
        self.publishers: List[str] = []

        self.rating: Optional[Tuple[Ratings, Any]] = None

        self.features: Dict[Features, Any] = {}

    @property
    def unique_id(self) -> Optional[str]:
        if not self.product_code:
            return None

        if self.region == Regions.JP:
            return self.product_code[3:-1]
        else:
            return self.product_code[4:-1]

    # def price(self, country: str) -> Price:
    #     return get_price(country=country, game=self)

    def url(self, country: str, lang: str = "en") -> Optional[str]:
        if not self.nsuid:
            return None

        return f"https://ec.nintendo.com/{country}/{lang}/titles/{self.nsuid}"

    def __repr__(self):
        return self.title
