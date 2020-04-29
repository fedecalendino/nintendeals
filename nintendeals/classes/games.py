from datetime import datetime
from typing import List

from nintendeals.api.prices import get_price
from nintendeals.classes.prices import Price
from nintendeals.constants import PLATFORMS, REGIONS
from nintendeals.exceptions import InvalidTitle, InvalidRegion, UnsupportedPlatform
from nintendeals import validate

ESHOP_URL = 'https://ec.nintendo.com/{country}/{lang}/titles/{nsuid}'


class Game:

    def __init__(
        self,
        title: str,
        region: str,
        platform: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        if not title: raise InvalidTitle(title)
        if not region in REGIONS: raise InvalidRegion(region)
        if not platform in PLATFORMS: raise UnsupportedPlatform(platform)

        self.title: str = title
        self.region: str = region
        self.platform: str = platform
        self.nsuid: str = nsuid
        self.product_code: str = product_code

        self.na_slug: str = None

        self.genres: List[str] = []
        self.languages: List[str] = []
        self.players: int = 0
        self.release_date: datetime = None
        self.size: int = None

        self.amiibo: bool = None
        self.demo: bool = None
        self.description: str = None
        self.developer: str = None
        self.dlc: bool = None
        self.free_to_play: bool = None
        self.game_vouchers: bool = None
        self.iaps: bool = None
        self.local_multiplayer: bool = None
        self.online_play: bool = None
        self.publisher: str = None
        self.save_data_cloud: bool = None
        self.voice_chat: str = None

    @property
    def unique_id(self) -> str:
        return self.product_code[-5:-1] if self.product_code else None

    def url(self, country: str, lang: str = "en") -> str:
        """
            Given a valid `country` code and an optional language it
        will provide a url that will redirect to this game's eShop page.

        Parameters
        ----------
        country: str
            Valid country code.
        lang: str (default: "en")
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

        validate.alpha_2(country)

        return ESHOP_URL.format(
            country=country,
            lang=lang,
            nsuid=self.nsuid
        )

    def price(self, country: str) -> Price:
        """
            Using the price API it will retrieve the pricing
        of the game in the given country. It will only work if
        the country is is under the region of the game.

        Parameters
        ----------
        country: str
            Valid country code.

        Returns
        -------
        nintendeals.classes.prices.Price
            Pricing of this game in the given country.
        """
        return get_price(country, self)

    def __repr__(self):
        return self.title
