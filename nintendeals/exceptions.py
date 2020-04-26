from nintendeals.constants import REGIONS


class InvalidAlpha2Code(ValueError):
    def __init__(self, country_code: str):
        super().__init__(
            f"{country_code} is not a valid alpha-2 code."
            " Visit https://www.iso.org/obp/ui/#search/code"
            " for a list of valid codes."
        )


class InvalidNsuidFormat(ValueError):
    def __init__(self, nsuid: str):
        super().__init__(
            f"{nsuid} is not a valid nsuid,"
            f" a 14 digit string was expected."
        )


class InvalidRegion(ValueError):
    def __init__(self, region: str):
        super().__init__(
            f"{region} is not a valid Nintendo region,"
            f" the valid regions are: {', '.join(REGIONS)}."
        )


class UnsupportedPlatform(ValueError):
    def __init__(self, platform: str):
        super().__init__(f"The platform {platform} is not supported.")


class NsuidMismatch(ValueError):
    def __init__(self, nsuids: tuple):
        super().__init__(f"Two or more nsuids mismatched unexpectedly: {nsuids}")


class InvalidTitle(TypeError):
    def __init__(self, title: str):
        super().__init__(
            f"The title '{title}' cannot be"
            f" an empty string or None"
        )
