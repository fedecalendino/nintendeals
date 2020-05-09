from datetime import datetime
from typing import List, Optional

from nintendeals import validate
from nintendeals.api.prices import get_price
from nintendeals.classes.prices import Price


class Game:

    @validate.title
    @validate.region
    @validate.nsuid(nullable=True)
    def __init__(
        self,
        title: str,
        region: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        self.title: str = title
        self.region: str = region
        self.nsuid: str = nsuid
        self.product_code: str = product_code

        self.na_slug: str = None

        self.description: str = None
        self.developer: str = None
        self.genres: List[str] = []
        self.languages: List[str] = []
        self.players: int = 0
        self.publisher: str = None
        self.release_date: datetime = None
        self.size: int = None

        # Features
        self.amiibo: bool = None
        self.demo: bool = None
        self.dlc: bool = None
        self.free_to_play: bool = None
        self.iaps: bool = None

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
        nintendeals.classes.prices.Price
            Pricing of this game in the given country.

        Raises
        -------
        nintendeals.exceptions.InvalidAlpha2Code
            The `country` wasn't a valid alpha-2 code.
        """
        return get_price(country=country, game=self)

    @property
    def unique_id(self) -> Optional[str]:
        raise NotImplementedError()

    def url(self, *, country: str, lang: str = "en") -> str:
        raise NotImplementedError()

    def __repr__(self):
        return self.title
