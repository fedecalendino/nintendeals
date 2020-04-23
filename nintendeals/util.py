# TODO document
from urllib import parse


def unquote(string: str) -> str:
    return parse.unquote(string.replace("\\u00", "%"))
