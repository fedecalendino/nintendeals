import logging
import re
from datetime import datetime

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
from commons.keys import ID
from commons.keys import NA
from commons.keys import NSUIDS
from commons.keys import NUMBER_OF_PLAYERS
from commons.keys import PUBLISHED_BY_NINTENDO
from commons.keys import REGION
from commons.keys import RELEASE_DATE
from commons.keys import TITLE_EN
from commons.keys import WEBSITES


LOG = logging.getLogger('nintendo.na')

AMERICA = REGIONS[NA]


def fetch_games(system, published_by_nintendo=False):
    additional = '&publisher=nintendo' if published_by_nintendo else ''

    start = 0
    limit = 200

    while True:
        if published_by_nintendo:
            LOG.info('Loading {} games published by nintendo (from {} to {})'.format(system, start, start + limit))
        else:
            LOG.info('Loading {} games (from {} to {})'.format(system, start, start + limit))

        url = AMERICA[API].format(system=SYSTEMS[system][ALIAS][NA], offset=start, limit=limit, additional=additional)
        response = requests.get(url)

        json = response.json()

        if not json.get('games', {}).get('game'):
            break

        for game in json['games']['game']:
            yield game

        start += limit


def _list_games(system, only_published_by_nintendo=False):
    for data in fetch_games(system, published_by_nintendo=only_published_by_nintendo):
        title = data.get('title', '').replace('Â®', '®').replace('Ã©', 'é').replace('Ã', 'Û')
        nsuid = data.get('nsuid')

        if nsuid in [None, 'HAC']:
            continue

        if not data.get('game_code'):
            LOG.info('{} has no game id'.format(title))
            continue

        game_id = get_game_id(nsuid=nsuid, game_id=data.get('game_code'), system=system)

        if len(game_id) < 6:
            continue

        game = Game.create(game_id, system)

        game[TITLE_EN] = title
        game[NSUIDS][NA] = nsuid
        game[CATEGORIES] = get_categories(data.get('categories', {}).get('category', []))

        if only_published_by_nintendo:
            game[PUBLISHED_BY_NINTENDO] = True

        try:
            game[NUMBER_OF_PLAYERS] = int(re.sub('[^0-9]*', '', data.get('number_of_players', '0')))
        except:
            game[NUMBER_OF_PLAYERS] = 0

        game[RELEASE_DATE] = datetime.strptime(data.get('release_date'), '%b %d, %Y').strftime('%Y-%m-%d')

        slug = data.get('slug')

        for country, details in COUNTRIES.items():
            if details[REGION] == NA and WEBSITES in details:
                game[WEBSITES][country] = details[WEBSITES].format(slug)

        yield game


def list_games(system):
    by_nintendo = []

    for game in _list_games(system, only_published_by_nintendo=True):
        by_nintendo.append(game[ID])

        yield game

    for game in _list_games(system):
        if game[ID] in by_nintendo:
            continue

        yield game
