from nintendeals.commons.enumerates import Platforms


class NAeShop:

    FORMAT = "https://www.nintendo.com/{lang}_{country}/games/detail/{slug}"

    def __init__(self, game: "Game"):
        self.game = game

    @property
    def ca_en(self) -> str:
        return NAeShop.FORMAT.format(
            lang="en",
            country="CA",
            slug=self.game.slug
        )

    @property
    def ca_fr(self) -> str:
        return NAeShop.FORMAT.format(
            lang="fr",
            country="CA",
            slug=self.game.slug
        )

    @property
    def us_en(self) -> str:
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
    def at_de(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="at",
            slug=self.game.slug
        )

    @property
    def be_fr(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="be",
            lang="fr",
            slug=self.game.slug
        )

    @property
    def be_nl(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="be",
            lang="nl",
            slug=self.game.slug
        )

    @property
    def ch_de(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="de",
            slug=self.game.slug
        )

    @property
    def ch_fr(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="fr",
            slug=self.game.slug
        )

    @property
    def ch_it(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ch",
            lang="it",
            slug=self.game.slug
        )

    @property
    def de_de(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="de",
            slug=self.game.slug
        )

    @property
    def es_es(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="es",
            slug=self.game.slug
        )

    @property
    def fr_fr(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="fr",
            slug=self.game.slug
        )

    @property
    def it_it(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="it",
            slug=self.game.slug
        )

    @property
    def nl_nl(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="nl",
            slug=self.game.slug
        )

    @property
    def pt_pt(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="pt",
            slug=self.game.slug
        )

    @property
    def ru_ru(self) -> str:
        return EUeShop.FORMAT_LANG.format(
            domain="ru",
            lang="-",
            slug=self.game.slug
        )

    @property
    def uk_en(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="co.uk",
            slug=self.game.slug
        )

    @property
    def za_en(self) -> str:
        return EUeShop.FORMAT_NO_LANG.format(
            domain="co.za",
            slug=self.game.slug
        )

    @property
    def au_en(self) -> str:
        if self.game.platform != Platforms.NINTENDO_SWITCH:
            raise ValueError("Only available for Nintendo Switch games")

        return EUeShop.FORMAT_ALT.format(
            country="AU",
            lang="en",
            nsuid=self.game.nsuid
        )

    @property
    def nz_en(self) -> str:
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
    def jp_jp(self) -> str:
        if self.game.platform == Platforms.NINTENDO_3DS:
            return JPeShop.OLD_FORMAT.format(nsuid=self.game.nsuid)

        if self.game.platform == Platforms.NINTENDO_WIIU:
            return JPeShop.OLD_FORMAT.format(nsuid=self.game.nsuid)

        return JPeShop.NEW_FORMAT.format(nsuid=self.game.nsuid)
