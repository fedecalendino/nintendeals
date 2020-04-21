from urllib import parse


def unquote(string: str) -> str:
    """
    Clean up a string of undesired url encodings.

    Parameters
    ----------
    string: str
        string to decode.

    Returns
    -------
        sparkly clean string ✨.
    """
    return parse.unquote(string.replace("\\u00", "%"))


def clean(string: str) -> str:
    """
    Clean up a string of undesired characters.

    Parameters
    ----------
    string: str
        string to clean up.

    Returns
    -------
        sparkly clean string ✨.

    """
    undesired = ["™", ]

    for char in undesired:
        string = string.replace(char, "")

    return string
