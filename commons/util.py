from commons.config import SYSTEMS
from commons.keys import CUT
from commons.keys import TAG


def format_float(value, total_digits=0):
    value = '%.2f' % value
    zeroes_to_add = total_digits - len(value) if total_digits > len(value) else 0

    return '{}{}'.format('0' * zeroes_to_add, value)


def build_game_id(game_id, system):
    if '/' in game_id:
        return game_id

    system = SYSTEMS[system]
    tag = system[TAG]
    cut = system[CUT]

    return '{}/{}'.format(tag, game_id[cut:-1]).upper()
