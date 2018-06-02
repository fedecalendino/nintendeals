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


LOG = logging.getLogger('nintendo.eu')


REGION = REGIONS[EU_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def find_games(system, start=0):
    LOG.info('Looking for games {} to {} in EU'.format(start, start + 10))

    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][EU_], start=start))
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

        nsuid = data['nsuid_txt'][0]

        if GAMES_DB.find_by_region_and_nsuid(EU_, nsuid) is not None:
            continue

        game_id = "{}-{}".format(system, data['product_code_txt'][0][-5:-1])

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
                release_date_: data['dates_released_dts'][0][:10],
                number_of_players_: data['players_to'] if 'players_to' in data else 0
            }

            LOG.info("New game {} ({}) found on EU".format(title, game[id_]))
        else:
            if EU_ in game[ids_] and game[ids_][EU_] != nsuid:
                print('Found duplicate for {} on EU: {}'.format(game_id, title))
                continue

        game[title_] = title
        game[ids_][EU_] = nsuid
        game[genres_] = categories

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

    if total > start + 10:
        games.update(find_games(system, start + 10))

    return games
