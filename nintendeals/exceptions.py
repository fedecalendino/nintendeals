from nintendeals.constants import REGIONS


class InvalidAlpha2Code(ValueError):
    def __init__(self, country_code: str):
        super().__init__(
            f"{country_code} is not a valid alpha-2 code. Visit"
            f" https://iso.org/obp/ui/#search/code for a list of valid codes."
        )


class InvalidNsuidFormat(ValueError):
    def __init__(self, nsuid: str):
        super().__init__(
            f"{nsuid} is not a valid nsuid, a 14 digit string was expected."
        )


class InvalidRegion(ValueError):
    def __init__(self, region: str):
        super().__init__(
            f"{region} is not a valid Nintendo region, the valid regions"
            f" are: {', '.join(REGIONS)}."
        )


class InvalidTitle(TypeError):
    def __init__(self):
        super().__init__("The title cannot be an empty string or None")
