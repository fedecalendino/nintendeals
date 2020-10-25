from nintendeals.commons.enumerates import Platforms, Regions, eShops

NA = {
    eShops.UnitedStates_EN: "https://www.nintendo.com/en_US/games/detail/{slug}",
    eShops.Canada_EN: "https://www.nintendo.com/en_CA/games/detail/{slug}",
    eShops.Canada_FR: "https://www.nintendo.com/fr_CA/games/detail/{slug}",
}

EU = {
    eShops.Austria_DE: "https://www.nintendo.at{slug}",
    eShops.Belgium_FR: "https://www.nintendo.be/fr{slug}",
    eShops.Belgium_NL: "https://www.nintendo.be/nl{slug}",
    eShops.France_FR: "https://www.nintendo.fr{slug}",
    eShops.Germany_DE: "https://www.nintendo.de{slug}",
    eShops.Italy_IT: "https://www.nintendo.it{slug}",
    eShops.Netherlands_NL: "https://www.nintendo.nl{slug}",
    eShops.Portugal_PT: "https://www.nintendo.pt{slug}",
    eShops.Russia_RU: "https://www.nintendo.ru/-{slug}",
    eShops.SouthAfrica_EN: "https://www.nintendo.co.za{slug}",
    eShops.Spain_ES: "https://www.nintendo.es{slug}",
    eShops.Switzerland_DE: "https://www.nintendo.ch/de{slug}",
    eShops.Switzerland_FR: "https://www.nintendo.ch/fr{slug}",
    eShops.Switzerland_IT: "https://www.nintendo.ch/it{slug}",
    eShops.UnitedKingdom_EN: "https://www.nintendo.co.uk{slug}",
}

EU_ALT = {
    eShops.Australia_EN: "https://ec.nintendo.com/AU/en/titles/{nsuid}",
    eShops.NewZealand_EN: "https://ec.nintendo.com/NZ/en/titles/{nsuid}",
}


class eShopURL:

    @staticmethod
    def na(game: "Game", website: eShops):
        if website not in NA:
            raise ValueError("Website unavailable for NA region")

        return NA[website].format(slug=game.slug)

    @staticmethod
    def eu(game: "Game", website: eShops):
        if website not in EU and website not in EU_ALT:
            raise ValueError("Website unavailable for EU region")

        if website in EU_ALT:
            if game.platform != Platforms.NINTENDO_SWITCH:
                raise ValueError("Only available for Nintendo Switch games")

            return EU_ALT[website].format(nsuid=game.nsuid)
        else:
            return EU[website].format(slug=game.slug)

    @staticmethod
    def jp(game: "Game", website: eShops):
        if website != eShops.Japan_JP:
            raise ValueError("Website unavailable for JP region")

        if game.platform == Platforms.NINTENDO_SWITCH:
            url = "https://store-jp.nintendo.com/list/software/{nsuid}.html"
        else:
            url = "https://www.nintendo.co.jp/titles/{nsuid}"

        return url.format(nsuid=game.nsuid)

    @staticmethod
    def get(game: "Game", website: eShops):
        return {
            Regions.NA: eShopURL.na,
            Regions.EU: eShopURL.eu,
            Regions.JP: eShopURL.jp,
        }.get(game.region)(game, website)
