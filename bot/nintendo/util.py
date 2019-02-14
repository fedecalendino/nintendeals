from commons.keys import N3DS
from commons.keys import SWITCH

alts = {
    '70010000001367': 'NX/AF3B',    # Doom
    '70010000004562': 'NX/AEYU2',   # NA: Johnny Turbo's Arcade: Gate Of Doom
    '70010000002341': 'NX/AB382',   # NA: NBA 2K18 Legend Edition
    '70010000002344': 'NX/AB383',   # NA: NBA 2K18 Legend Edition Gold
    '70010000012840': 'NX/AQ7P',    # NA: The Messenger
    '70010000001536': 'NX/AB382',   # JP: NBA 2K18 Legend Edition
    '70010000002346': 'NX/AB383',   # JP: NBA 2K18 Legend Edition Gold
    '70010000002608': 'NX/BAAN',    # JP: Mario + Rabbids Kingdom Battle
    '70010000012941': 'NX/AQ9F',    # EU: A Case of Distrust
    '70010000002023': 'NX/AM28',    # JP: Arena of Valor
    '70010000011429': 'NX/AQNJ',    # EU: Spider Solitaire F
    '70010000001345': 'NX/AENW',    # EU: SUPERBEAT: XONiC
    '70010000000854': 'NX/AN2B',    # EU: Let's Sing 2018
    '70010000009417': 'NX/AMUS',    # JP: Fallen Legion
    '70010000003655': 'NX/AK75',    # EU: Tricky Towers
    '70010000002022': 'NX/AM28',    # NA: Arena of Valor
    '70010000001641': 'NX/AHAB',    # NA: Party Planet
    '70010000007283': 'NX/AHAB2',   # EU: 30-in-1 Game Collection: Volume 1
    '70010000001906': 'NX/AHKT',    # EU: Timber Tennis: Versus
}

category_map = {
    'role-playing': 'rpg',
    'board_game': 'board game',
    'first_person_shooter': 'shooter',
    'puzzles': 'puzzle',
}


def get_game_id(nsuid, game_id, system):
    if nsuid in alts:
        return alts[nsuid]

    init = -5

    if system == SWITCH:
        tag = 'NX'
    elif system == N3DS:
        tag = '3DS'
        init = -4
    else:
        raise Exception()

    return '{}/{}'.format(tag, game_id[init:-1]).upper()


def get_categories(categories):
    if type(categories) == str:
        categories = [categories.lower()]
    else:
        categories = [cat.lower() for cat in categories]

    return sorted([category_map.get(cat, cat) for cat in categories])


def parse_jp_date(date):
    if '.' not in date:
        return date

    parts = date.split('.')

    return '{}-{:02d}-{:02d}'.format(int(parts[0]), int(parts[1]), int(parts[2]))
