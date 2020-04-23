import re

from pycountry import countries

from nintendeals.exceptions import InvalidAlpha2Code, InvalidNsuidFormat

NSUID_REGEX = re.compile(r"\d001\d{10}")


def alpha_2(code: str):
    """
    Validates that the given `code` is a valid alpha-2 country code.
    Full list of valid codes at https://www.iso.org/obp/ui/#search/code.

    Parameters
    ----------
    code: str
        code to validate.

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


def nsuid_format(string: str):
    """
    Validates that the given `string` matches the format of a valid nsuid.
    Valid nsuid follow the "[0-9]001[0-9]{10}" regular expression.

    Parameters
    ----------
    string: str
        string to validate.

    Examples
    -------
    >>> nsuid_format("70010000000450")  # ✅️
    >>> nsuid_format("70010000000")     # ❌️
    >>> nsuid_format(70010000000)       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidAlpha2Code
        The `string` wasn't a valid formatted as a valid nsuid.
    """
    if not isinstance(string, str):
        raise InvalidNsuidFormat(string)

    match = NSUID_REGEX.match(string)

    if match is None:
        raise InvalidNsuidFormat(string)
