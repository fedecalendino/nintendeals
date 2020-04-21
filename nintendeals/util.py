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
