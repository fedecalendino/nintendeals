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
        nsuid: str,
        product_code: str,
        title: str,
        region: str,
        platform: str,
    ):
        assert nsuid
        assert product_code
        assert title
        assert region in REGIONS
        assert platform in PLATFORMS

        self.nsuid: str = nsuid
        self.product_code: str = product_code
        self.title: str = title
        self.region: str = region
        self.platform: str = platform

        self.na_slug: str = None

        self.genres: List[str] = []
        self.languages: List[str] = []
        self.players: int = 0
        self.release_date: datetime = None
        self.size: int = []

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
        return self.product_code[-5:-1]

    def url(self, country: str, lang: str = "en") -> str:
        country = countries.get(alpha_2=country)
        assert country

        return ESHOP_URL.format(
            country=country.alpha_2,
            lang=lang,
            nsuid=self.nsuid
        )

    def price(self, country: str) -> Price:
        return get_price(country, [self.nsuid])

    def __repr__(self):
        return f'{self.nsuid} > {self.title}'

