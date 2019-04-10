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
from commons.keys import NA
from commons.keys import REGION
from commons.keys import WEBSITE


LOG = logging.getLogger('nintendo.na')

AMERICA = REGIONS[NA]

FIXES = {
    "70010000019385": "70010000000529", 
    "Splatoon 2 + Nintendo Switch Online Individual Membership (12 Months)" : "Splatoon 2"
}


def fetch_games(system, published_by_nintendo=False):
    additional = '&publisher=nintendo' if published_by_nintendo else ''

    start = 0
    limit = 200

    while True:
        if published_by_nintendo:
            LOG.info(f'Loading {system} games published by nintendo (from {start} to {start + limit})')
        else:
            LOG.info(f'Loading {system} games  (from {start} to {start + limit})')

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
        title = data.get('title', '')
        nsuid = data.get('nsuid')

        if nsuid in [None, 'HAC']:
            continue

        if not data.get('game_code'):
            # LOG.info('{} has no game id'.format(title))
            continue

        game_id = get_game_id(nsuid=nsuid, game_id=data.get('game_code'))

        game = Game(_id=game_id, system=system)

        game.titles[NA] = FIXES.get(title, title)
        game.nsuids[NA] = FIXES.get(nsuid, nsuid)

        game.categories = get_categories(data.get('categories', {}).get('category', []))

        game.free_to_play = data.get('free_to_start', 'false') == 'true'

        if only_published_by_nintendo:
            game.published_by_nintendo = True

        for country, details in COUNTRIES.items():
            if details[REGION] == NA and WEBSITE in details:
                game.websites[country] = details[WEBSITE].format(nsuid=nsuid)

        try:
            game.number_of_players = int(re.sub('[^0-9]*', '', data.get('number_of_players', '0')))
        except:
            game.number_of_players = 0

        try:
            game.release_dates[NA] = datetime.strptime(data.get('release_date'), '%b %d, %Y')
        except:
            continue

        yield game


def list_games(system):
    by_nintendo = []

    for game in _list_games(system, only_published_by_nintendo=True):
        by_nintendo.append(game.id)

        yield game

    for game in _list_games(system):
        if game.id in by_nintendo:
            continue

        yield game
