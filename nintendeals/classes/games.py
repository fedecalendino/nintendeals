from datetime import datetime
from typing import List

from pycountry import countries

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
        self.players: int = 0
        self.publisher: str = None
        self.release_date: datetime = None
        self.save_data_cloud: bool = None
        self.size: int = None
        self.slug: str = None
        self.voice_chat: str = None

        self.genres: List[str] = []
        self.languages: List[str] = []

    def url(self, country: str, lang: str = "en") -> str:
        country = countries.get(alpha_2=country)
        assert country

        return ESHOP_URL.format(
            country=country.alpha_2,
            lang=lang,
            nsuid=self.nsuid
        )

    def __repr__(self):
        return f'{self.nsuid} > {self.title}'

