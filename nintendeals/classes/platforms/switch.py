from nintendeals.classes.games import Game
from typing import Optional
from nintendeals import validate

ESHOP_URL = 'https://ec.nintendo.com/{country}/{lang}/titles/{nsuid}'


class SwitchGame(Game):

    platform = "Nintendo Switch"

    def __init__(
        self,
        title: str,
        region: str,
        nsuid: str = None,
        product_code: str = None,
    ):
        super().__init__(
            title=title,
            region=region,
            nsuid=nsuid,
            product_code=product_code
        )

        self.game_vouchers: bool = None
        self.local_multiplayer: bool = None
        self.nso_required: bool = None
        self.save_data_cloud: bool = None
        self.voice_chat: str = None

    @property
    def unique_id(self) -> Optional[str]:
        if not self.product_code:
            return None

        return self.product_code[-5:-1]

    @validate.country
    def url(self, *, country: str, lang: str = "en") -> str:
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

        return ESHOP_URL.format(
            country=country,
            lang=lang,
            nsuid=self.nsuid
        )
