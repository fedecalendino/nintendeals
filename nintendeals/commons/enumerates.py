from enum import Enum


class Features(str, Enum):
    AMIIBO = "Amiibo Supported"
    DEMO = "Demo Available"
    DLC = "DLC Available"
    NSO_REQUIRED = "Nintendo Switch Online Required"
    SAVE_DATA_CLOUD = "Save Data Cloud Supported"
    VOICE_CHAT = "Voice Chat Supported"

    def __str__(self):
        return str(self.value)


class Platforms(str, Enum):
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
