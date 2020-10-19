from enum import Enum


class Features(str, Enum):
    GAME_VOUCHERS = "Game Vouchers"
    LOCAL_MULTIPLAYER = "Local Multiplayer"
    NSO_REQUIRED = "Nintendo Switch Online Required"
    SAVE_DATA_CLOUD = "Save Data Cloud"
    VOICE_CHAT = "Voice Chat"

    def __str__(self):
        return str(self.value)


class Platforms(str, Enum):
    NINTENDO_3DS = "Nintendo 3DS"
    NINTENDO_SWITCH = "Nintendo Switch"
    NINTENDO_WII_U = "Nintendo Wii U"

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
