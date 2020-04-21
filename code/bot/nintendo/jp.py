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

NSUID = 'NSUID'


def fetch_games(system):
    LOG.info(f'Loading {system} games')

    if system == N3DS:
        url = "https://www.nintendo.co.jp/data/software/xml/3ds_pkg_dl.xml"
    else:
        url = f'https://www.nintendo.co.jp/data/software/xml/{system.lower()}.xml'

    title_info_list = xmltodict.parse(requests.get(url).text)['TitleInfoList']['TitleInfo']

    for game in title_info_list:
        game[NSUID] = game['LinkURL'].split('/')[-1]
        yield game[NSUID], game


def extract_game_data(system, data):
    nsuid = data.get(NSUID)
    game_code = get_game_id(nsuid=nsuid, game_id=data.get('InitialCode'))

    if len(nsuid) < 10 or len(game_code) < 7:
        return None

    game = Game(_id=game_code, system=system)

    game.titles[JP] = data.get('TitleName').title()
    game.nsuids[JP] = nsuid
    game.published_by_nintendo = data.get('MakerName', '') == '任天堂'
    game.free_to_play = data.get('Price', '') == '無料'

    game.websites[JP] = JAPAN[DETAILS][system].format(nsuid=nsuid)

    try:
        game.release_dates[JP] = datetime.strptime(data.get('SalesDate'), '%Y.%m.%d')
    except:
        return None

    return game


def list_new_games(system, games_on_db):
    for nsuid, data in fetch_games(system):
        if nsuid in games_on_db:
            continue

        game = extract_game_data(system, data)

        if game:
            if game.id in ['3DS/AL8']:
                continue

            LOG.info(f'Found new game {game} {nsuid}')

            yield nsuid, game
        else:
            LOG.error(f'Failed to extract data for game with nsuid {nsuid}')
