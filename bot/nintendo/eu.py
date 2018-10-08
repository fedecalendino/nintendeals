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

# Local
from bot.nintendo.util import *


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

        # Getting nsuids for switch (7) or 3ds (5)
        nsuid = [code for code in data['nsuid_txt'] if code[0] in ['5', '7']][0]

        # Checking for game_id fixes
        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]
        else:
            game_id = parse_game_id(product_ids[0], system)

        game = GAMES_DB.load(game_id)

        title = data['title'].replace('Â®', '®').replace('Ã©', 'é')

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
        game[genres_] = parse_categories(data['game_categories_txt'])

        game[publisher_] = data.get('publisher')

        # Setting number of players
        number_of_players = data['players_to'] if 'players_to' in data else 0

        if game.get(number_of_players_) is None or number_of_players > 0:
            game[number_of_players_] = number_of_players

        # Setting game features
        game[features_] = {
            feat_demo_: data.get('demo_availability'),
            feat_dlc_: data.get('add_on_content_b'),
            feat_internet_: data.get('internet'),
            feat_local_play_: data.get('local_play'),
            feat_players_: game[number_of_players_],
            feat_nfc_: data.get('near_field_comm_b')
        }

        if system == SWITCH_:
            game[features_][feat_free_to_play_] = data.get('price_sorting_f', 0) == 0
            game[features_][feat_cloud_saves_] = data.get('cloud_saves_b')
            game[features_][feat_hd_rumble_] = data.get('hd_rumble_b')
            game[features_][feat_nso_] = data.get('paid_subscription_required_b')
            game[features_][feat_voice_chat_] = data.get('voice_chat_b')
            game[features_][feat_ir_camera_] = data.get('ir_motion_camera_b')
        elif system == N3DS_:
            game[features_][feat_mii_] = data.get('mii_support')
            game[features_][feat_spotpass_] = data.get('spot_pass')
            game[features_][feat_streetpass_] = data.get('street_pass')
            game[features_][feat_download_play_] = data.get('download_play')
            game[features_][feat_motion_control_] = data.get('motion_control_3ds')

        # Setting release date if missing
        if game.get(release_date_) is None:
            game[release_date_] = data['dates_released_dts'][0][:10]

        # Setting if nintendo is publisher if missing
        published_by_nintendo = data.get('publisher') == 'Nintendo'

        if game.get(published_by_nintendo_) is None or (not game[published_by_nintendo_] and published_by_nintendo):
            game[published_by_nintendo_] = published_by_nintendo

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {id_: nsuid, countries_: {}}  # Creating price object if missing

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == EU_:

                # Adding placeholders for regional prices
                if country not in price[countries_]:
                    price[countries_][country] = None

                # Updating regional websites
                if websites_ in country_details:
                    game[websites_][country] = country_details[websites_].format(data['url'].rsplit('/', 1)[-1])

        games[game_id] = game

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    if total > start + limit:
        games.update(find_games(system, start + limit, limit))

    return games
