from datetime import datetime
from typing import List, Optional

from nintendeals import validate
from nintendeals.api.prices import get_price
from nintendeals.classes.prices import Price


class Game:

    platform = None

    @validate.title
    @validate.region
    @validate.nsuid(nullable=True)
    def __init__(
        self,
        region: str,
        title: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        self.region: str = region
        self.title: str = title
        self.nsuid: str = nsuid
        self.product_code: str = product_code

        self.slug: str = None

        self.description: str = None
        self.developer: str = None
        self.genres: List[str] = []
        self.languages: List[str] = []
        self.megabytes: int = None
        self.players: int = 0
        self.publisher: str = None
        self.rating: str = None
        self.release_date: datetime = None

        # Images
        self.banner_img: str = None
        self.cover_img: str = None

        # Features
        self.amiibo: bool = None
        self.demo: bool = None
        self.dlc: bool = None
        self.free_to_play: bool = None
        self.iaps: bool = None

    @property
    def unique_id(self) -> Optional[str]:
        raise NotImplementedError()

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
        nintendeals.exceptions.InvalidAlpha2Code
            The `country` wasn't a valid alpha-2 code.
        """
        if not self.nsuid:
            return None

        return f"https://ec.nintendo.com/{country}/{lang}/titles/{self.nsuid}"

    def __repr__(self):
        return self.title
