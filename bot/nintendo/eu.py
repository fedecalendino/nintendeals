import logging

import requests

from bot.nintendo.util import get_categories
from bot.nintendo.util import get_game_id

from commons.classes import Game
from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS
from commons.keys import ALIAS
from commons.keys import API
from commons.keys import CATEGORIES
from commons.keys import EU
from commons.keys import NSUIDS
from commons.keys import NUMBER_OF_PLAYERS
from commons.keys import PUBLISHED_BY_NINTENDO
from commons.keys import REGION
from commons.keys import RELEASE_DATE
from commons.keys import TITLE_EN
from commons.keys import WEBSITES


LOG = logging.getLogger('nintendo.eu')

EUROPE = REGIONS[EU]


def fetch_games(system):
    start = 0
    limit = 200

    while True:
        LOG.info('Loading {} games (from {} to {})'.format(system, start, start + limit))

        url = EUROPE[API].format(system=SYSTEMS[system][ALIAS][EU], start=start, limit=limit)
        response = requests.get(url)

        json = response.json().get('response').get('docs', [])

        if not len(json):
            break

        for game in json:
            yield game

        start = start + limit


def list_games(system):
    for data in fetch_games(system):
        title = data.get('title').replace('Â®', '®').replace('Ã©', 'é').replace('Ã', 'Û')

        if not data.get('nsuid_txt'):
            LOG.info('{} has no nsuid'.format(title))
            continue

        for product_id in data.get('product_code_txt', []):
            if '-' not in product_id:
                break
        else:
            LOG.info('{} is not a valid game'.format(title))
            continue

        # Getting nsuids for switch (7) or 3ds (5)
        nsuid = [code for code in data['nsuid_txt'] if code[0] in ['5', '7']][0]
        game_id = get_game_id(nsuid=nsuid, game_id=product_id, system=system)

        game = Game.create(game_id, system)

        game[TITLE_EN] = title
        game[NSUIDS][EU] = nsuid
        game[CATEGORIES] = get_categories(data.get('game_categories_txt', []))

        game[PUBLISHED_BY_NINTENDO] = data.get('publisher', '') == 'Nintendo'
        game[NUMBER_OF_PLAYERS] = data.get('players_to', 0)
        game[RELEASE_DATE] = data.get('dates_released_dts')[0][:10]

        slug = data['url'].rsplit('/', 1)[-1]

        for country, details in COUNTRIES.items():
            if details[REGION] == EU and WEBSITES in details:
                game[WEBSITES][country] = details[WEBSITES].format(slug)

        yield game
