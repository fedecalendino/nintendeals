import re

from pycountry import countries

from nintendeals import exceptions
from nintendeals.constants import REGIONS

NSUID_REGEX = re.compile(r"[5-7]00\d{11}")


def _validate_nsuid(nsuid_: str, nullable: bool = False):
    if nullable and nsuid_ is None:
        return

    if not isinstance(nsuid_, str):
        raise exceptions.InvalidNsuidFormat(nsuid_)

    if not NSUID_REGEX.match(nsuid_):
        raise exceptions.InvalidNsuidFormat(nsuid_)


def _validate_game(game: "Game", nullable: bool = False):
    if nullable and game is None:
        return

    _validate_nsuid(game.nsuid)


def country(func):
    """
        Validates that the parameter `country` of the decorated function is
    a valid alpha-2 country code.
        Full list of valid codes at https://www.iso.org/obp/ui/#search/code.

    Examples
    -------
    >>> country="CZ"      # ✅️
    >>> country="XX"      # ❌️
    >>> country="ARG"     # ❌️
    >>> country=123       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidAlpha2Code
        The `code` wasn't a valid alpha-2 code.
    """
    def wrapper(*args, **kwargs):
        code_ = kwargs.get("country")
        country_ = countries.get(alpha_2=code_)

        if not country_:
            raise exceptions.InvalidAlpha2Code(code_)

        return func(*args, **kwargs)
    return wrapper


def region(func):
    """
        Validates that the parameter `region` of the decorated function is
    a valid Nintendo region.

    Examples
    -------
    >>> region="NA"    # ✅️
    >>> region="LA"    # ❌️
    >>> region="ASIA"  # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidRegion
        The `region` wasn't valid.
    """
    def wrapper(*args, **kwargs):
        region_ = kwargs.get("region")

        if region_ not in REGIONS:
            raise exceptions.InvalidRegion(region_)

        return func(*args, **kwargs)
    return wrapper


def title(func):
    """
        Validates that the parameter `title` of the decorated function is
    not empty or none.

    Examples
    -------
    >>> title="Super Mario Party"    # ✅️
    >>> title=""                     # ❌️
    >>> title=None                   # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidTitle
        The `title` wasn't valid.
    """
    def wrapper(*args, **kwargs):
        if not title:
            raise exceptions.InvalidTitle()

        return func(*args, **kwargs)
    return wrapper


def nsuids(nullable: bool = False):
    """
        Validates that all the nsuids in the parameter `nsuids` of the decorated
    function match the format of a valid nsuid.
        A valid nsuid follows the "[5-7]00[0-9]{11}" regular expression.

    Parameters
    ----------
    nullable: bool = False
        If true, an exception won't be raise if any nsuid is None.

    Examples
    -------
    >>> nsuids=["70010000000450"]  # ✅️
    >>> nsuids=["50010000000654"]  # ✅️
    >>> nsuids=["70010000000"]     # ❌️
    >>> nsuids=[50010000000]       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        Any of the `nsuids` was either none or had an invalid format.
    """
    def outer(func):
        def inner(*args, **kwargs):
            for nsuid_ in kwargs.get("nsuids", []):
                _validate_nsuid(nsuid_, nullable)

            return func(*args, **kwargs)
        return inner

    if callable(nullable):
        return outer(func=nullable)

    return outer


def nsuid(nullable: bool = False):
    """
        Validates that the parameter `nsuid` of the decorated function matches
    the format of a valid nsuid.
        A valid nsuid follows the "[5-7]00[0-9]{11}" regular expression.

    Parameters
    ----------
    nullable: bool = False
        If true, an exception won't be raise if the nsuid is None.

    Examples
    -------
    >>> nsuids=["70010000000450"]  # ✅️
    >>> nsuids=["50010000000654"]  # ✅️
    >>> nsuids=["70010000000"]     # ❌️
    >>> nsuids=[50010000000]       # ❌️

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The `nsuids` was either none or had an invalid format.
    """
    def outer(func):
        def inner(*args, **kwargs):
            nsuid_ = kwargs.get("nsuid")
            _validate_nsuid(nsuid_, nullable)

            return func(*args, **kwargs)
        return inner

    if callable(nullable):
        return outer(func=nullable)

    return outer


def games(nullable: bool = False):
    """
        Validates that all the games in the parameter `games` of the decorated
    function follow a list of restrictions.

    Parameters
    ----------
    nullable: bool = False
        If true, an exception won't be raise if any game is None.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        Any of the `games` had an nsuid that was either none or
    had an invalid format.
    """
    def outer(func):
        def inner(*args, **kwargs):
            for game_ in kwargs.get("games", []):
                _validate_game(game_, nullable)

            return func(*args, **kwargs)
        return inner

    if callable(nullable):
        return outer(func=nullable)

    return outer


def game(nullable: bool = False):
    """
        Validates that the parameter `game` of the decorated function follows
     a list of restrictions.

    Parameters
    ----------
    nullable: bool = False
        If true, an exception won't be raise if the game is None.

    Raises
    -------
    nintendeals.exceptions.InvalidNsuidFormat
        The `games` had an nsuid that was either none or had an invalid format.
    """
    def outer(func):
        def inner(*args, **kwargs):
            game_ = kwargs.get("game")
            _validate_game(game_, nullable)

            return func(*args, **kwargs)
        return inner

    if callable(nullable):
        return outer(func=nullable)

    return outer
