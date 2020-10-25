from enum import Enum


class Features(str, Enum):
    AMIIBO = "Amiibo Supported"
    DEMO = "Demo Available"
    DLC = "DLC Available"
    LOCAL_MULTIPLAYER = "Local Multiplayer Supported"
    GAME_VOUCHERS = "Game Vouchers Qualified"
    NSO_REQUIRED = "Nintendo Switch Online Required"
    SAVE_DATA_CLOUD = "Save Data Cloud Supported"
    VOICE_CHAT = "Voice Chat Supported"

    def __str__(self):
        return str(self.value)


class Platforms(str, Enum):
    NINTENDO_WIIU = "Nintendo Wii U"
    NINTENDO_3DS = "Nintendo 3DS"
    NINTENDO_SWITCH = "Nintendo Switch"

    def __str__(self):
        return str(self.value)


class Ratings(str, Enum):
    CERO = "CERO"  # JP
    ESRB = "ESRB"  # NA
    PEGI = "PEGI"  # EU

    def __str__(self):
        return str(self.value)


class Regions(str, Enum):
    NA = "NA"
    EU = "EU"
    JP = "JP"

    def __str__(self):
        return str(self.value)


class eShops(str, Enum):
    UnitedStates_EN = "en_US"
    Canada_EN = "en_CA",
    Canada_FR = "fr_CA",

    Austria_DE = "de_AT"
    Belgium_FR = "fr_BE"
    Belgium_NL = "nl_BE"
    France_FR = "fr_FR"
    Germany_DE = "de_DE"
    Italy_IT = "it_IT"
    Netherlands_NL = "nl_NL"
    Portugal_PT = "pt_PT"
    Russia_RU = "ru_RU"
    SouthAfrica_EN = "en_ZA"
    Spain_ES = "es_ES"
    Switzerland_DE = "de_CH"
    Switzerland_FR = "fr_CH"
    Switzerland_IT = "it_CH"
    UnitedKingdom_EN = "en_UK"

    Australia_EN = "en_AU"
    NewZealand_EN = "en_NZ"

    Japan_JP = "jp_JP"

    def __str__(self):
        return str(self.value)
