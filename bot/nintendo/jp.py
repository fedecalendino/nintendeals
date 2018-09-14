# Standard
import logging

# Dependencies
import re
import json
import requests
import xmltodict

# Modules
from bot.db.mongo import GamesDatabase
from bot.db.mongo import PricesDatabase

# Constants
from bot.commons.config import *
from bot.commons.keys import *

from bot.nintendo.commons import alt_versions


LOG = logging.getLogger('🎮.🇯🇵 ')


REGION = REGIONS[JP_]
LIST_API = REGION[api_]

GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def get_id_map(system):
    if system == N3DS_:
        url = "https://www.nintendo.co.jp/data/software/xml/3ds_pkg_dl.xml"
    else:
        url = 'https://www.nintendo.co.jp/data/software/xml/{}.xml'.format(system.lower())

    xml = requests.get(url).text

    game_list = xmltodict.parse(xml)

    id_map = {}

    for title_info in game_list['TitleInfoList']['TitleInfo']:
        if system == SWITCH_:
            game_id = "{}-{}".format(system, title_info['InitialCode'][-5:-1])
        elif system == N3DS_:
            game_id = "{}-{}".format(system, title_info['InitialCode'][-4:-1])
        else:
            raise Exception()

        rd = title_info['SalesDate']

        if '.' in rd:
            rd = rd.split('.')

            rd = '{}-{}-{}'.format(
                rd[0],
                '0' + rd[1] if len(rd[1]) == 1 else rd[1],
                '0' + rd[2] if len(rd[2]) == 1 else rd[2]
            )

        id_map[title_info['LinkURL'].rsplit('/', 1)[-1]] = {
            id_: game_id,
            title_jp_: title_info['TitleName'],
            release_date_: rd
        }

    return id_map


def find_games(system):

    id_map = get_id_map(system)

    games = {}

    for nsuid, info in id_map.items():

        game_id = info[id_]
        title_jp = info[title_jp_]
        release_date = info[release_date_]

        if GAMES_DB.find_by_region_and_nsuid(JP_, nsuid) is not None:
            continue

        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]

        game = GAMES_DB.load(game_id)

        url = REGION[details_][system].format(nsuid)

        if game is None:
            number_of_players = 0

            if system == SWITCH_:
                try:
                    details = requests.get(url).text
                    details = re.findall('NXSTORE\\.titleDetail\\.jsonData .*;', details)[0]
                    details = details.replace('NXSTORE.titleDetail.jsonData = ', '').replace(';', '')

                    data = json.loads(details)

                    number_of_players = max(data['player_number'].values())
                except:
                    pass

            game = {
                id_: game_id,
                ids_: {},
                websites_: {},
                system_: system,
                release_date_: release_date,
                number_of_players_: number_of_players
            }

            LOG.info('New game {} ({}) found on JP'.format(title_jp, game_id))
        else:
            if JP_ in game[ids_] and game[ids_][JP_] != nsuid:
                LOG.info('Found duplicate for {} on JP'.format(game_id))
                continue

        game[ids_][JP_] = nsuid
        game[title_jp_] = title_jp
        game[websites_][JP_] = url

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


