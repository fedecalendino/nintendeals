from bot.commons.keys import SWITCH_, N3DS_


def parse_game_id(game_id, system):
    if system == SWITCH_:
        return "{}-{}".format(system, game_id[-5:-1])
    elif system == N3DS_:
        return "{}-{}".format(system, game_id[-4:-1])
    else:
        raise Exception()


def parse_categories(categories):
    if type(categories) == str:
        categories = [categories]
    else:
        categories = [cat.lower() for cat in categories]

    categories.sort()

    return categories


def parse_jp_date(date):
    if '.' not in date:
        return date

    parts = date.split('.')

    return '{}-{}-{}'.format(
        parts[0],
        '0' + parts[1] if len(parts[1]) == 1 else parts[1],
        '0' + parts[2] if len(parts[2]) == 1 else parts[2]
    )
