from typing import Optional

from nintendeals.classes.games import Game


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
