from datetime import datetime
from bot.commons.keys import *


def format_float(value, total_digits=0):
    value = '%.2f' % value

    if total_digits == 0:
        return value
    else:
        return '0' * (total_digits - len(value)) + value


def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def get_title(game):
    if title_ in game:
        title = game[title_]
    else:
        title = game[title_jp_]

    return title. \
        replace('\'', ''). \
        replace('’', ''). \
        title(). \
        replace('Iii', 'III'). \
        replace('Ii', 'II')
