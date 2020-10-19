from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from nintendeals import validate
from nintendeals.api.prices import get_price
from nintendeals.commons import (
    Price,
    Features,
    Platforms,
    Ratings,
    Regions,
)


class Game:

    @validate.title
    @validate.nsuid(nullable=True)
    def __init__(
        self,
        *,
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
        self.developer: str = None
        self.publisher: str = None
        self.slug: str = None

        self.players: int = 0

        self.release_date: datetime = None

        self.genres: List[str] = []
        self.languages: List[str] = []

        self.features: Dict[Features, Any] = {}
        self.rating: Tuple[Ratings, Any] = (None, None)

    @property
    def unique_id(self) -> Optional[str]:
        if not self.product_code:
            return None

        return self.product_code[-5:-1]  # Switch code

    @validate.country
    def price(self, *, country: str) -> Price:
        """
            Using the price API it will retrieve the pricing
        of the game in the given country. It will only work if
        the country is is under the region of the game.

        Parameters
        ----------
        country: str
            Valid alpha-2 code of the country.

        Returns
        -------
        nintendeals.commons.Price
            Pricing of this game in the given country.

        Raises
        -------
        nintendeals.commons.InvalidAlpha2Code
            The `country` wasn't a valid alpha-2 code.
        """
        return get_price(country=country, game=self)

    @validate.country
    def url(self, *, country: str, lang: str = "en") -> Optional[str]:
        """
            Given a valid `country` code and an optional language it will
        provide a url (using the game's nsuid) that will redirect to the
        eShop page for this game.

        Parameters
        ----------
        country: str
            Valid alpha-2 code of the country.
        lang: str = "en"
            Valid iso-code for language.

        Returns
        -------
        str
            URL for the eShop of the game.

        Raises
        -------
        nintendeals.commons.InvalidAlpha2Code
            The `country` wasn't a valid alpha-2 code.
        """
        if not self.nsuid:
            return None

        return f"https://ec.nintendo.com/{country}/{lang}/titles/{self.nsuid}"

    def __repr__(self):
        return self.title
