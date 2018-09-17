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

        # Setting number of players
        number_of_players = data['players_to'] if 'players_to' in data else 0
        game[number_of_players_] = number_of_players

        game[features_] = {
            feat_demo_: data['demo_availability'] if 'demo_availability' in data else None,
            feat_dlc_: data['add_on_content_b'] if 'add_on_content_b' in data else None,
            feat_free_to_play_: data['price_sorting_f'] == 0,
            feat_internet_: data['internet'] if 'internet' in data else None,
            feat_local_play_: data['local_play'] if 'local_play' in data else None,
            feat_players_: number_of_players,
        }

        if system == SWITCH_:
            game[features_][feat_cloud_saves_] = data['cloud_saves_b'] if 'cloud_saves_b' in data else None
            game[features_][feat_hd_rumble_] = data['hd_rumble_b'] if 'hd_rumble_b' in data else None
            game[features_][feat_nso_] = data['paid_subscription_required_b'] if 'paid_subscription_required_b' in data else None
            game[features_][feat_voice_chat_] = data['voice_chat_b'] if 'voice_chat_b' in data else None

        # Setting release date
        game[release_date_] = data['dates_released_dts'][0][:10]

        # Setting published by nintendo
        if 'publisher' in data:
            game[published_by_nintendo_] = data['publisher'] == 'Nintendo'

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
