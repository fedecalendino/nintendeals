from typing import Optional

from nintendeals import validate
from nintendeals.classes.games import Game
from nintendeals.constants import NA, EU, JP


class N3dsGame(Game):

    platform = "Nintendo 3DS"

    def __init__(
        self,
        region: str,
        title: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        super().__init__(
            region=region,
            title=title,
            nsuid=nsuid,
            product_code=product_code
        )

        self.download_play: bool = None
        self.internet: bool = None
        self.motion_control: bool = None
        self.spot_pass: bool = None
        self.street_pass: bool = None
        self.virtual_console: bool = None

    @property
    def unique_id(self) -> Optional[str]:
        if not self.product_code:
            return None

        return self.product_code[-4:-1]

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

        if self.region == NA and self.slug:
            return f"https://www.nintendo.com/{lang}_{country}/games/detail/{self.slug}/"

        if self.region == EU and self.slug:
            if country == "GB":
                country = "CO.UK"

            if country == "ZA":
                country = "CO.ZA"

            return f"https://www.nintendo.{country.lower()}/{lang}{self.slug}"

        if self.region == JP:
            return f"https://www.nintendo.co.jp/titles/{self.nsuid}"

        return None
