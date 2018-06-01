# Standard
import logging

# Dependencies
import re
import json
import requests
import xmltodict

# Modules
from app.db.mongo import GamesDatabase
from app.db.mongo import PricesDatabase

# Constants
from app.commons.config import *
from app.commons.keys import *

from app.nintendo.commons import alt_versions


LOG = logging.getLogger('nintendo.jp')


REGION = REGIONS[JP_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def get_id_map(system):
    url = 'https://www.nintendo.co.jp/data/software/xml/{}.xml'.format(system.lower())

    xml = requests.get(url).text

    game_list = xmltodict.parse(xml)

    id_map = {}

    for title_info in game_list['TitleInfoList']['TitleInfo']:
        id_map[title_info['LinkURL'].rsplit('/', 1)[-1]] = title_info['InitialCode'][-5:]

    return id_map


def find_games(system):

    id_map = get_id_map(system)

    games = {}

    for nsuid, game_id in id_map.items():

        if GAMES_DB.find_by_region_and_nsuid(JP_, nsuid) is not None:
            continue

        game_id = "{}-{}".format(system, game_id)

        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]

        game = GAMES_DB.load(game_id)

        url = REGION[details_].format(nsuid)

        if game is None:
            details = requests.get(url).text
            details = re.findall('NXSTORE\\.titleDetail\\.jsonData .*;', details)[0]
            details = details.replace('NXSTORE.titleDetail.jsonData = ', '').replace(';', '')

            data = json.loads(details)

            try:
                players = max(data['player_number'].values())
            except:
                players = 0

            game = {
                id_: game_id,
                ids_: {},
                title_jp_: data['formal_name'],
                websites_: {},
                system_: system,
                release_date_: data['release_date_on_eshop'],
                number_of_players_: players
            }

            LOG.info("New game {} ({}) found on JP".format(game[title_jp_], game[id_]))
        else:
            if JP_ in game[ids_] and game[ids_][JP_] != nsuid:
                print('Found duplicate for {} on JP'.format(game_id))
                continue

        game[websites_][JP_] = url
        game[ids_][JP_] = nsuid

        games[game_id] = game

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {
                id_: nsuid,
                countries_: {}
            }

        price[countries_][JP_] = None

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    return games


