import re

from pycountry import countries

from nintendeals.constants import REGIONS
from nintendeals.exceptions import (
    InvalidAlpha2Code,
    InvalidNsuidFormat,
    InvalidRegion,
)

NSUID_REGEX = re.compile(r"\d001\d{10}")


def alpha_2(code: str):
    """
        Validates that the given `code` is a valid alpha-2 country code.
    Full list of valid codes at https://www.iso.org/obp/ui/#search/code.

    Parameters
    ----------
    code: str
        Code to validate.

    Examples
    -------
    >>> alpha_2("CZ")      # ✅️
    >>> alpha_2("XX")      # ❌️
    >>> alpha_2("ARG")     # ❌️
    >>> alpha_2(123)       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidAlpha2Code
        The `code` wasn't a valid alpha-2 code.
    """
    country = countries.get(alpha_2=code)

    if not country:
        raise InvalidAlpha2Code(code)


def nsuid_format(nsuid: str):
    """
        Validates that the given `nsuid` matches the format of a valid nsuid.
    Valid nsuid follow the "[0-9]001[0-9]{10}" regular expression.

    Parameters
    ----------
    nsuid: str
        Nsuid to validate.

    Examples
    -------
    >>> nsuid_format("70010000000450")  # ✅️
    >>> nsuid_format("70010000000")     # ❌️
    >>> nsuid_format(70010000000)       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The `string` wasn't a valid formatted as a valid nsuid.
    """
    if not isinstance(nsuid, str):
        raise InvalidNsuidFormat(nsuid)

    if not NSUID_REGEX.match(nsuid):
        raise InvalidNsuidFormat(nsuid)


def nintendo_region(region: str):
    """
        Validates that the given `region` is a valid Nintendo region.

    Parameters
    ----------
    region: str
        Region to validate.

    Examples
    -------
    >>> nintendo_region("NA")    # ✅️
    >>> nintendo_region("LA")    # ❌️
    >>> nintendo_region("ASIA")  # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidRegion
        The `region` wasn't a valid region.
    """
    if region not in REGIONS:
        raise InvalidRegion(region)


def _nsuid(nsuid: str):
    if not isinstance(nsuid, str):
        raise InvalidNsuidFormat(nsuid)

    if not NSUID_REGEX.match(nsuid):
        raise InvalidNsuidFormat(nsuid)


def _game(game: "Game"):
    _nsuid(game.nsuid)


def country(func):
    def wrapper(*args, **kwargs):
        code_ = kwargs.get("country")
        country_ = countries.get(alpha_2=code_)

        if not country_:
            raise InvalidAlpha2Code(code_)

        return func(*args, **kwargs)
    return wrapper


def nsuids(func):
    def wrapper(*args, **kwargs):
        list(map(_nsuid, kwargs.get("nsuids", [])))

        return func(*args, **kwargs)
    return wrapper


def games(func):
    def wrapper(*args, **kwargs):
        list(map(_game, kwargs.get("games", [])))

        return func(*args, **kwargs)
    return wrapper


def game(func):
    def wrapper(*args, **kwargs):
        _game(kwargs["game"])

        return func(*args, **kwargs)
    return wrapper
