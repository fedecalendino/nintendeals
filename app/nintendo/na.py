# Standard
from datetime import datetime
import re
import logging

# Dependencies
import requests

# Modules
from app.db.mongo import GamesDatabase
from app.db.mongo import PricesDatabase

# Constants
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('nintendo.na')


REGION = REGIONS[NA_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def find_games(system, limit=100, offset=0):
    LOG.info('Looking for games {} to {} in NA'.format(offset, offset + limit))

    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][NA_], limit=limit, offset=offset))
    json = r.json()

    total = json['filter']['total']

    if total == 0:
        return {}

    games = {}

    for data in json['games']['game']:
        if 'nsuid' not in data:
            continue

        nsuid = data['nsuid']

        if GAMES_DB.find_by_region_and_nsuid(NA_, nsuid) is not None:
            continue

        game_id = "{}-{}".format(system, data['game_code'][-5:])

        game = GAMES_DB.load(game_id)

        title = data['title']
        title = title.replace('Â®', '®').replace('Ã©', 'é')

        if game is None:
            release_date = datetime.strptime(data['release_date'], '%b %d, %Y').strftime('%Y-%m-%d')
            number_of_players = re.sub('[^0-9]*', '', data['number_of_players'])

            categories = data['categories']['category']

            if type(categories) == str:
                categories = [categories]

            categories.sort()

            game = {
                id_: game_id,
                ids_: {},
                title_: title,
                system_: system,
                websites_: {},
                release_date_: release_date,
                number_of_players_: int(number_of_players) if len(number_of_players) else 0,
                genres_: [cat.lower() for cat in categories]
            }

            LOG.info("New game {} ({}) found on NA".format(game[title_], game[id_]))
        else:
            if NA_ in game[ids_] and game[ids_][NA_] != nsuid:
                print('Found duplicate for {} on NA: {}'.format(game_id, title))
                continue

        game[ids_][NA_] = nsuid

        games[game_id] = game

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {
                id_: nsuid,
                countries_: {}
            }

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == NA_:
                if country not in price[countries_]:
                    price[countries_][country] = None

                if websites_ in country_details and 'slug' in data:
                    game[websites_][country] = country_details[websites_].format(data['slug'])

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    if total > limit + offset:
        games.update(find_games(system, limit, offset + limit))

    return games


