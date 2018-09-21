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

from bot.nintendo.commons import *

# Local
from bot.nintendo.util import *


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
        nsuid = title_info['LinkURL'].rsplit('/', 1)[-1]

        id_map[nsuid] = {
            id_: parse_game_id(title_info['InitialCode'], system),
            title_jp_: title_info['TitleName'],
            release_date_: parse_jp_date(title_info['SalesDate']),
            publisher_: title_info['MakerName']
        }

    return id_map


def find_games(system):

    id_map = get_id_map(system)

    games = {}

    for nsuid, info in id_map.items():
        title_jp = info[title_jp_]
        release_date = info[release_date_]

        # Checking for game_id fixes
        if nsuid in alt_versions:
            game_id = alt_versions[nsuid]
        else:
            game_id = info[id_]

        game = GAMES_DB.load(game_id)

        url = REGION[details_][system].format(nsuid)

        if game is None:
            game = {
                id_: game_id,
                ids_: {},
                websites_: {},
                system_: system
            }

            LOG.info('New game {} ({}) found on JP'.format(title_jp, game_id))
        else:
            if JP_ in game[ids_] and game[ids_][JP_] != nsuid:
                LOG.info('Found duplicate for {} on JP'.format(game_id))
                continue

        if features_ not in game and system == SWITCH_:
            try:
                content = requests.get(url).text
                details = re.findall('NXSTORE\\.titleDetail\\.jsonData .*;', content)[0]
                details = details.replace('NXSTORE.titleDetail.jsonData = ', '').replace(';', '')

                data = json.loads(details)

                game[features_] = {
                    feat_cloud_saves_: None if 'cloud_backup_type' not in data else data['cloud_backup_type'] == 'supported',
                    feat_nso_: None if 'features' not in data else 2001 in [feature['id'] for feature in data['features']],
                    feat_demo_: False if 'demos' not in data else len(data.get('demos')) > 0,
                    feat_dlc_: '<span>追加コンテンツ</span>' in content
                }

                players = [0]

                for ps in data['player_number'].values():
                    players.append(ps)

                # Setting number of players if missing or not available
                if game.get(number_of_players_) is None or game[number_of_players_] == 0:
                    game[number_of_players_] = max(players)
            except Exception as e:
                print(e)

        game[ids_][JP_] = nsuid
        game[title_jp_] = title_jp

        # Updating regional websites
        game[websites_][JP_] = url

        # Setting release date if missing
        if game.get(release_date_) is None:
            game[release_date_] = release_date

        # Setting if nintendo is publisher if missing
        published_by_nintendo = info[publisher_] == '任天堂'

        if game.get(published_by_nintendo_) is None or (not game[published_by_nintendo_] and published_by_nintendo):
            game[published_by_nintendo_] = published_by_nintendo

        price = PRICES_DB.load(nsuid)

        if price is None:
            price = {id_: nsuid, countries_: {}}  # Creating price object if missing

        # Adding placeholders for regional prices
        price[countries_][JP_] = None

        games[game_id] = game

        GAMES_DB.save(game)
        PRICES_DB.save(price)

    return games


