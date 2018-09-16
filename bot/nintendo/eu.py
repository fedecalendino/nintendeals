# Standard
import logging

# Dependencies
import requests

# Modules
from bot.db.mongo import GamesDatabase
from bot.db.mongo import PricesDatabase

# Constants
from bot.commons.config import *
from bot.commons.keys import *

from bot.nintendo.commons import *


LOG = logging.getLogger('🎮.🇪🇺 ')


REGION = REGIONS[EU_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def find_games(system, start=0, limit=200):
    LOG.info('Looking for games {} to {} in EU'.format(start, start + limit))

    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][EU_], start=start, limit=limit))
    json = r.json()

    total = json['response']['numFound']

    if total == 0:
        return {}

    games = {}

    for data in json['response']['docs']:
        if 'nsuid_txt' not in data:
            continue

        if 'product_code_txt' not in data:
            continue

        product_ids = [
            prod_id
            for prod_id in data['product_code_txt']
            if prod_id[:3] in ['CTR', 'HAC'] and '-' not in prod_id
        ]

        if len(product_ids) == 0:
            continue

        nsuid = [code for code in data['nsuid_txt'] if code[0] in ['5', '7']][0]

        # if GAMES_DB.find_by_region_and_nsuid(EU_, nsuid) is not None:
        #    continue

        if system == SWITCH_:
            game_id = '{}-{}'.format(system, product_ids[0][-5:-1])
        elif system == N3DS_:
            game_id = '{}-{}'.format(system, product_ids[0][-4:-1])
        else:
            raise Exception()

        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]

        game = GAMES_DB.load(game_id)

        title = data['title']
        title = title.replace('Â®', '®').replace('Ã©', 'é')

        categories = [cat.lower() for cat in data['game_categories_txt']]
        categories.sort()
        
        if game is None:
            game = {
                id_: game_id,
                ids_: {},
                websites_: {},
                system_: system,
            }

            LOG.info('New game {} ({}) found on EU'.format(title, game[id_]))
        else:
            if EU_ in game[ids_] and game[ids_][EU_] != nsuid:
                LOG.info('Found duplicate for {} on EU: {}'.format(game_id, title))
                continue

        game[title_] = title
        game[ids_][EU_] = nsuid
        game[genres_] = categories

        # Setting release date
        release_date = data['dates_released_dts'][0][:10]

        if release_date_ not in game:
            game[release_date_] = release_date
        elif game[release_date_] is None and release_date:
            game[release_date_] = release_date

        # Setting published by nintendo
        by_nintendo = 'publisher' in data and data['publisher'] == 'Nintendo'

        if published_by_nintendo_ not in game:
            game[published_by_nintendo_] = by_nintendo
        elif not game[published_by_nintendo_] and by_nintendo:
            game[published_by_nintendo_] = by_nintendo

        # Setting number of players
        number_of_players = data['players_to'] if 'players_to' in data else 0

        if number_of_players_ not in game:
            game[number_of_players_] = number_of_players
        elif game[number_of_players_] == 0 and number_of_players != 0:
            game[number_of_players_] = number_of_players

        games[game_id] = game

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {
                id_: nsuid,
                countries_: {}
            }

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == EU_:

                if country not in price[countries_]:
                    price[countries_][country] = None

                if websites_ in country_details:
                    game[websites_][country] = country_details[websites_].format(data['url'].rsplit('/', 1)[-1])

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    if total > start + limit:
        games.update(find_games(system, start + limit, limit))

    return games
