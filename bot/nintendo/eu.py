import logging
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
from commons.keys import EU
from commons.keys import REGION
from commons.keys import WEBSITE


LOG = logging.getLogger('nintendo.eu')

EUROPE = REGIONS[EU]


FSID_FIXER = {
    '1388917': (['HACPAD8HA'], ['70070000003542'])  # Starlink: Battle for Atlas
}


def fetch_games(system):
    start = 0
    limit = 200

    while True:
        LOG.info(f'Loading {system} games (from {start} to {start + limit})')

        url = EUROPE[API].format(system=SYSTEMS[system][ALIAS][EU], start=start, limit=limit)
        response = requests.get(url)

        json = response.json().get('response').get('docs', [])

        if not len(json):
            break

        for game in json:
            try:
                yield game.get('nsuid_txt')[0], game
            except:
                continue

        start = start + limit


def extract_game_data(system, data):
    title = data.get('title')
    fs_id = data.get('fs_id')

    if fs_id in FSID_FIXER:
        data['product_code_txt'], data['nsuid_txt'] = FSID_FIXER.get(fs_id)

    try:
        # Getting nsuids for switch (7) or 3ds (5)
        nsuid, product_id = [
            (nsuid_txt, product_code_txt)
                for nsuid_txt, product_code_txt in zip(data.get('nsuid_txt', []), data.get('product_code_txt', []))
                    if nsuid_txt[0] in ['5', '7']
        ][0]
    except:
        return None

    game_code = get_game_id(nsuid=nsuid, game_id=product_id)

    if len(nsuid) < 10 or len(game_code) < 7:
        return None

    game = Game(_id=game_code, system=system)

    if game.id == '3DS/JCV':
        print('')

    game.titles[EU] = title
    game.nsuids[EU] = nsuid

    game.categories = get_categories(data.get('game_categories_txt', []))

    game.free_to_play = data.get('price_sorting_f', 1) == 0

    game.published_by_nintendo = data.get('publisher', '') == 'Nintendo'
    game.number_of_players = data.get('players_to', 0)

    for country, details in COUNTRIES.items():
        if details[REGION] == EU and WEBSITE in details:
            game.websites[country] = details[WEBSITE].format(nsuid=nsuid)

    try:
        game.release_dates[EU] = datetime.strptime(data.get('dates_released_dts')[0][:10], '%Y-%m-%d')
    except:
        return None

    return game


def list_new_games(system, games_on_db):
    for nsuid, data in fetch_games(system):
        if nsuid in games_on_db:
            continue

        game = extract_game_data(system, data)

        if game:
            LOG.info(f'Found new game {game}')

            yield nsuid, game
        else:
            LOG.error(f'Failed to extract data for game with nsuid {nsuid}')
