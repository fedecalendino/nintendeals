import logging
from datetime import datetime

import requests
import xmltodict

from bot.nintendo.util import get_game_id

from commons.classes import Game

from commons.config import REGIONS

from commons.keys import API
from commons.keys import DETAILS
from commons.keys import JP
from commons.keys import N3DS


LOG = logging.getLogger('nintendo.jp')

JAPAN = REGIONS[JP]
LIST_API = JAPAN[API]


def get_id_map(system):
    if system == N3DS:
        url = "https://www.nintendo.co.jp/data/software/xml/3ds_pkg_dl.xml"
    else:
        url = f'https://www.nintendo.co.jp/data/software/xml/{system.lower()}.xml'

    game_list = xmltodict.parse(requests.get(url).text)

    return {
        title_info['LinkURL'].rsplit('/', 1)[-1]: title_info
            for title_info in game_list['TitleInfoList']['TitleInfo']
    }


def list_games(system):
    LOG.info(f'Loading {system} games')

    id_map = get_id_map(system)

    for nsuid, info in id_map.items():
        game_id = get_game_id(nsuid=nsuid, game_id=info.get('InitialCode'))

        game = Game(_id=game_id, system=system)

        game.titles[JP] = info.get('TitleName').title()
        game.nsuids[JP] = nsuid
        game.websites[JP] = JAPAN[DETAILS][system].format(nsuid=nsuid)

        game.published_by_nintendo = info.get('MakerName', '') == '任天堂'

        try:
            game.release_dates[JP] = datetime.strptime(info.get('SalesDate'), '%Y.%m.%d')
        except:
            continue

        yield game
