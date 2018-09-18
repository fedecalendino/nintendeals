# Standard
from datetime import datetime
import re
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

# Local
from bot.nintendo.util import *


LOG = logging.getLogger('🎮.🇺🇸 ')


REGION = REGIONS[NA_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def _find_games(system, limit=200, offset=0, published_by_nintendo=False):
    LOG.info('Looking for games {} to {} in NA'.format(offset, offset + limit))

    r = requests.get(LIST_API.format(
        system=SYSTEMS[system][system_][NA_],
        limit=limit,
        offset=offset,
        additional='&publisher=nintendo' if published_by_nintendo else ''
    ))
    json = r.json()

    total = json['filter']['total']

    if total == 0:
        return {}

    games = {}

    for data in json['games']['game']:
        if 'nsuid' not in data and 'game_code' not in data:
            continue

        if 'nsuid' not in data and 'game_code' in data:
            data['nsuid'] = data['game_code']

        if data['nsuid'] == 'HAC':
            continue

        nsuid = data['nsuid']

        # Checking for game_id fixes
        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]
        else:
            game_id = parse_game_id(data['game_code'], system)

        # Loading game from database
        game = GAMES_DB.load(game_id)

        title = data['title'].replace('Â®', '®').replace('Ã©', 'é')

        if game is None:
            game = {
                id_: game_id,
                ids_: {},
                system_: system,
                websites_: {},
            }

            LOG.info("New game {} ({}) found on NA".format(title, game[id_]))
        else:
            if NA_ in game[ids_] and game[ids_][NA_] != nsuid:
                LOG.info('Found duplicate for {} on NA: {}'.format(game_id, title))
                continue

        game[title_] = title
        game[ids_][NA_] = nsuid
        game[genres_] = parse_categories(data['categories']['category'])

        # Setting number of players if missing or not available
        if game.get(number_of_players_) is None or game[number_of_players_] == 0:
            number_of_players = re.sub('[^0-9]*', '', data['number_of_players'])

            game[number_of_players_] = int(number_of_players) if len(number_of_players) else 0

        # Setting release date if missing
        if game.get(release_date_) is None:
            game[release_date_] = datetime.strptime(data['release_date'], '%b %d, %Y').strftime('%Y-%m-%d')

        # Setting if nintendo is publisher if missing
        if game.get(published_by_nintendo_) is None or (not game[published_by_nintendo_] and published_by_nintendo):
            game[published_by_nintendo_] = published_by_nintendo

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {id_: nsuid, countries_: {}}  # Creating price object if missing

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == NA_:

                # Adding placeholders for regional prices
                if country not in price[countries_]:
                    price[countries_][country] = None

                # Updating regional websites
                if websites_ in country_details and 'slug' in data:
                    game[websites_][country] = country_details[websites_].format(data['slug'])

        games[game_id] = game

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    if total > limit + offset:
        games.update(_find_games(system, limit, offset + limit))

    return games


def find_games(system, limit=200, offset=0):
    _find_games(system, limit, offset, False)
    _find_games(system, limit, offset, True)
