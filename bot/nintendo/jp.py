import logging

import requests
import xmltodict

from bot.nintendo.util import get_game_id
from bot.nintendo.util import parse_jp_date

from commons.classes import Game
from commons.config import REGIONS
from commons.keys import API
from commons.keys import DETAILS
from commons.keys import JP
from commons.keys import N3DS
from commons.keys import NSUIDS
from commons.keys import PUBLISHED_BY_NINTENDO
from commons.keys import RELEASE_DATE
from commons.keys import TITLE_JP
from commons.keys import WEBSITES


LOG = logging.getLogger('nintendo.jp')

REGION = REGIONS[JP]
LIST_API = REGION[API]


def get_id_map(system):
    if system == N3DS:
        url = "https://www.nintendo.co.jp/data/software/xml/3ds_pkg_dl.xml"
    else:
        url = 'https://www.nintendo.co.jp/data/software/xml/{}.xml'.format(system.lower())

    xml = requests.get(url).text

    game_list = xmltodict.parse(xml)

    id_map = {}

    for title_info in game_list['TitleInfoList']['TitleInfo']:
        nsuid = title_info['LinkURL'].rsplit('/', 1)[-1]

        id_map[nsuid] = {
            'InitialCode': title_info.get('InitialCode'),
            'TitleName': title_info.get('TitleName'),
            'SalesDate': parse_jp_date(title_info.get('SalesDate')),
            'MakerName': title_info.get('MakerName', '')
        }

    return id_map


def list_games(system):
    LOG.info('Loading {} games '.format(system))

    id_map = get_id_map(system)

    for nsuid, info in id_map.items():
        title_jp = info['TitleName']
        game_id = get_game_id(nsuid=nsuid, game_id=info.get('InitialCode'), system=system)

        url = REGION[DETAILS][system].format(nsuid)

        game = Game.create(game_id, system)

        game[NSUIDS][JP] = nsuid
        game[TITLE_JP] = title_jp
        game[WEBSITES][JP] = url

        game[RELEASE_DATE] = info['SalesDate']
        game[PUBLISHED_BY_NINTENDO] = info['MakerName'] == '任天堂'

        yield game
