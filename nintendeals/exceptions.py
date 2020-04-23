class InvalidAlpha2Code(ValueError):
    def __init__(self, country_code: str):
        super().__init__(
            f"{country_code} is not a valid alpha-2 code. "
            "Visit https://www.iso.org/obp/ui/#search/code for a list of valid codes."
        )


class InvalidNsuidFormat(ValueError):
    def __init__(self, nsuid: str):
        super().__init__(
            f"{nsuid} is not a valid nsuid, "
            "a 14 digit string was expected."
        )
