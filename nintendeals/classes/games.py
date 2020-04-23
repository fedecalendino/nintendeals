from datetime import datetime
from typing import List

from pycountry import countries

from nintendeals.api.prices import get_price
from nintendeals.classes.prices import Price
from nintendeals.constants import PLATFORMS, REGIONS

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
        assert title
        assert region in REGIONS
        assert platform in PLATFORMS

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
        if not self.nsuid:
            return None

        country = countries.get(alpha_2=country)
        assert country

        return ESHOP_URL.format(
            country=country.alpha_2,
            lang=lang,
            nsuid=self.nsuid
        )

    def price(self, country: str) -> Price:
        return get_price(country, self)

    def __repr__(self):
        return self.title
