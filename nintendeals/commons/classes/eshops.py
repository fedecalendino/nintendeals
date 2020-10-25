from nintendeals.commons.enumerates import Platforms


class NAeShop:

    FORMAT = "https://www.nintendo.com/{lang}_{country}/games/detail/{slug}"

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def en_CA(self) -> str:
        return NAeShop.FORMAT.format(
            lang="en",
            country="CA",
            slug=self.game.slug
        )

    @property
    def fr_CA(self) -> str:
        return NAeShop.FORMAT.format(
            lang="fr",
            country="CA",
            slug=self.game.slug
        )

    @property
    def en_US(self) -> str:
        return NAeShop.FORMAT.format(
            lang="en",
            country="US",
            slug=self.game.slug
        )


class EUeShop:

    FORMAT_NO_LANG = "https://www.nintendo.{domain}{slug}"
    FORMAT_LANG = "https://www.nintendo.{domain}/{lang}{slug}"

    FORMAT_ALT = "https://ec.nintendo.com/{country}/{lang}/titles/{nsuid}"

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def de_AT(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="at",
            slug=self.game.slug
        )

    @property
    def fr_BE(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="be",
            lang="fr",
            slug=self.game.slug
        )

    @property
    def nl_BE(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="be",
            lang="nl",
            slug=self.game.slug
        )

    @property
    def de_CH(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="de",
            slug=self.game.slug
        )

    @property
    def fr_CH(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="fr",
            slug=self.game.slug
        )

    @property
    def it_CH(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="it",
            slug=self.game.slug
        )

    @property
    def de_DE(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="de",
            slug=self.game.slug
        )

    @property
    def es_ES(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="es",
            slug=self.game.slug
        )

    @property
    def fr_FR(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="fr",
            slug=self.game.slug
        )

    @property
    def it_IT(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="it",
            slug=self.game.slug
        )

    @property
    def nl_NL(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="nl",
            slug=self.game.slug
        )

    @property
    def pt_PT(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="pt",
            slug=self.game.slug
        )

    @property
    def ru_RU(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ru",
            lang="-",
            slug=self.game.slug
        )

    @property
    def en_UK(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="co.uk",
            slug=self.game.slug
        )

    @property
    def en_ZA(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="co.za",
            slug=self.game.slug
        )

    @property
    def en_AU(self) -> str:
        if self.game.platform != Platforms.NINTENDO_SWITCH:
            raise ValueError("Only available for Nintendo Switch games")

        return EUeShop.FORMAT_ALT.format(
            country="AU",
            lang="en",
            nsuid=self.game.nsuid
        )

    @property
    def en_NZ(self) -> str:
        if self.game.platform != Platforms.NINTENDO_SWITCH:
            raise ValueError("Only available for Nintendo Switch games")

        return EUeShop.FORMAT_ALT.format(
            country="NZ",
            lang="en",
            nsuid=self.game.nsuid
        )


class JPeShop:

    NEW_FORMAT = "https://store-jp.nintendo.com/list/software/{nsuid}.html"
    OLD_FORMAT = "https://www.nintendo.co.jp/titles/{nsuid}"

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def jp_JP(self) -> str:
        if self.game.platform == Platforms.NINTENDO_3DS:
            return JPeShop.OLD_FORMAT.format(nsuid=self.game.nsuid)

        if self.game.platform == Platforms.NINTENDO_WIIU:
            return JPeShop.OLD_FORMAT.format(nsuid=self.game.nsuid)

        return JPeShop.NEW_FORMAT.format(nsuid=self.game.nsuid)
