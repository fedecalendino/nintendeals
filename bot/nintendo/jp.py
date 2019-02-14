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


LOG = logging.getLogger('nintendo.jp')

JAPAN = REGIONS[JP]
LIST_API = JAPAN[API]


def get_id_map(system):
    if system == N3DS:
        url = "https://www.nintendo.co.jp/data/software/xml/3ds_pkg_dl.xml"
    else:
        url = 'https://www.nintendo.co.jp/data/software/xml/{}.xml'.format(system.lower())

    game_list = xmltodict.parse(requests.get(url).text)

    return {title_info['LinkURL'].rsplit('/', 1)[-1]: title_info
                for title_info in game_list['TitleInfoList']['TitleInfo']}


def list_games(system):
    LOG.info('Loading {} games '.format(system))

    id_map = get_id_map(system)

    for nsuid, info in id_map.items():
        game_id = get_game_id(nsuid=nsuid, game_id=info.get('InitialCode'))

        game = Game(_id=game_id, system=system)

        game.titles[JP] = info.get('TitleName').title()
        game.nsuids[JP] = nsuid
        game.websites[JP] = JAPAN[DETAILS][system].format(nsuid)
        game.release_dates[JP] = parse_jp_date(info.get('SalesDate'))

        game.published_by_nintendo = info.get('MakerName', '') == '任天堂'

        yield game
