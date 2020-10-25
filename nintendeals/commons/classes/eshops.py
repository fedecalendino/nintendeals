from nintendeals.commons.enumerates import Platforms


class NAeShop:

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def en_US(self) -> str:
        return f"https://www.nintendo.com/en_US/games/detail/{self.game.slug}"

    @property
    def en_CA(self) -> str:
        return f"https://www.nintendo.com/en_CA/games/detail/{self.game.slug}"

    @property
    def fr_CA(self) -> str:
        return f"https://www.nintendo.com/fr_CA/games/detail/{self.game.slug}"


class EUeShop:

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def de_AT(self) -> str:
        return f"https://www.nintendo.at{self.game.slug}"

    @property
    def fr_BE(self) -> str:
        return f"https://www.nintendo.be/fr{self.game.slug}"

    @property
    def nl_BR(self) -> str:
        return f"https://www.nintendo.be/nl{self.game.slug}"

    @property
    def fr_FR(self) -> str:
        return f"https://www.nintendo.fr{self.game.slug}"

    @property
    def de_DE(self) -> str:
        return f"https://www.nintendo.de{self.game.slug}"

    @property
    def it_IT(self) -> str:
        return f"https://www.nintendo.it{self.game.slug}"

    @property
    def nl_NL(self) -> str:
        return f"https://www.nintendo.nl{self.game.slug}"

    @property
    def pt_PT(self) -> str:
        return f"https://www.nintendo.pt{self.game.slug}"

    @property
    def ru_RU(self) -> str:
        return f"https://www.nintendo.ru/-{self.game.slug}"

    @property
    def en_ZA(self) -> str:
        return f"https://www.nintendo.co.za{self.game.slug}"

    @property
    def es_ES(self) -> str:
        return f"https://www.nintendo.es{self.game.slug}"

    @property
    def de_CH(self) -> str:
        return f"https://www.nintendo.ch/de{self.game.slug}"

    @property
    def fr_CH(self) -> str:
        return f"https://www.nintendo.ch/fr{self.game.slug}"

    @property
    def it_CH(self) -> str:
        return f"https://www.nintendo.ch/it{self.game.slug}"

    @property
    def en_UK(self) -> str:
        return f"https://www.nintendo.co.uk{self.game.slug}"

    @property
    def en_AU(self) -> str:
        if self.game.platform != Platforms.NINTENDO_SWITCH:
            raise ValueError("Only available for Nintendo Switch games")

        return f"https://ec.nintendo.com/AU/en/titles/{self.game.nsuid}"

    @property
    def en_NZ(self) -> str:
        if self.game.platform != Platforms.NINTENDO_SWITCH:
            raise ValueError("Only available for Nintendo Switch games")

        return f"https://ec.nintendo.com/NZ/en/titles/{self.game.nsuid}"


class JPeShop:

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def jp_JP(self) -> str:
        if self.game.platform == Platforms.NINTENDO_SWITCH:
            url = "https://store-jp.nintendo.com/list/software/{nsuid}.html"
        else:
            url = "https://www.nintendo.co.jp/titles/{nsuid}"

        return url.format(nsuid=self.game.nsuid)

