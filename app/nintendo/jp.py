# Standard
import logging

# Dependencies
import re
import json
import requests
import xmltodict

# Constants
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('nintendo.jp')

REGION = REGIONS[JP_]
LIST_API = REGION[api_]


def get_id_map(system):
    url = 'https://www.nintendo.co.jp/data/software/xml/{}.xml'.format(system.lower())

    xml = requests.get(url).text

    game_list = xmltodict.parse(xml)

    id_map = {}

    for title_info in game_list['TitleInfoList']['TitleInfo']:
        id_map[title_info['LinkURL'].rsplit('/', 1)[-1]] = title_info['InitialCode'][-5:]

    return id_map


def get_sales_ids(system, id_map):
    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][JP_]))
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text.lower())

    new_map = {}

    for url in urls:
        id = url.rsplit('/', 1)[-1]

        new_map[id] = id_map[id]

    return new_map


def get_deals(system):

    id_map = get_id_map(system)
    id_map = get_sales_ids(system, id_map)

    games = {}

    for jp_id, game_id in id_map.items():
        url = REGION[details_].format(jp_id)

        details = requests.get(url).text
        details = re.findall('NXSTORE\\.titleDetail\\.jsonData .*;', details)[0]
        details = details.replace('NXSTORE.titleDetail.jsonData = ', '').replace(';', '')

        data = json.loads(details)

        game_id = "{}-{}".format(system, game_id)

        try:
            players = max(data['player_number'].values())
        except:
            players = 0

        game = {
            id_: game_id,
            ids_: {
                JP_: jp_id
            },
            title_jp_: data['formal_name'],
            websites_: {
                JP_: url
            },
            system_: system,
            release_date_: data['release_date_on_eshop'],
            number_of_players_: players
        }

        games[game_id] = game

    return games


