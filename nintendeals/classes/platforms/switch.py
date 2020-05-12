from typing import Optional

from nintendeals.classes.games import Game


class SwitchGame(Game):

    platform = "Nintendo Switch"

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
