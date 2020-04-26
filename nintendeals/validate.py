import re

from pycountry import countries

from nintendeals.constants import PLATFORMS, REGIONS
from nintendeals.exceptions import (
    InvalidAlpha2Code,
    InvalidNsuidFormat,
    InvalidRegion,
    UnsupportedPlatform,
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

    match = NSUID_REGEX.match(nsuid)

    if match is None:
        raise InvalidNsuidFormat(nsuid)


def supported_platform(platform: str):
    """
        Validates that the given `platform` is supported by this library.

    Parameters
    ----------
    platform: str
        Platform to validate.

    Examples
    -------
    >>> supported_platform("Nintendo Switch")  # ✅️
    >>> supported_platform("Nintendo 3DS")     # ❌️
    >>> supported_platform("Microsoft XBox")   # ❌️

    Raises
    -------
    nintendeals.exceptions.UnsupportedPlaform
        The `platform` wasn't supported.
    """
    if platform not in PLATFORMS:
        raise UnsupportedPlatform(platform)


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
