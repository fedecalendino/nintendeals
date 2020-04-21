import logging
import re
import string
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from bot.nintendo.util import get_categories
from bot.nintendo.util import get_game_id
from commons.classes import Game
from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS
from commons.keys import ALIAS
from commons.keys import API
from commons.keys import DATA
from commons.keys import NA
from commons.keys import REGION
from commons.keys import WEBSITE

LOG = logging.getLogger('nintendo.na')

AMERICA = REGIONS[NA]

FIXES = {
    "70010000019385": "70010000000529", 
    "Splatoon 2 + Nintendo Switch Online Individual Membership (12 Months)": "Splatoon 2"
}

CACHE = set()


def fetch_games(system):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.nintendo.com',
        'Referer': 'https://www.nintendo.com/games/game-guide/',
        'DNT': '1',
        'Host': 'u3b6gr4ua3-dsn.algolia.net',
        'Accept-Language': 'en-us',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
        'Accept-Encoding': 'br, gzip, deflate',
        'Connection': 'keep-alive',
    }

    params = (
        ('x-algolia-agent', 'Algolia for vanilla JavaScript (lite) 3.22.1;JS Helper 2.20.1'),
        ('x-algolia-application-id', 'U3B6GR4UA3'),
        ('x-algolia-api-key', '9a20c93440cf63cf1a7008d75f7438bf'),
    )

    data = """
        {
            "requests": [
                {
                    "indexName": "noa_aem_game_en_us",
                    "params": "query={query}&hitsPerPage=200&maxValuesPerFacet=30&page={page}",
                    "facetFilters": [["platform:{system}"]]
                }
            ]
        }
    """.replace('{system}', SYSTEMS[system][ALIAS][NA])

    for query in string.ascii_lowercase + string.digits:
        page = 0

        while True:
            LOG.info(f'Fetching games from page {page} for query "{query}"')

            response = requests.post(
                url=AMERICA[API],
                headers=headers,
                params=params,
                data=data.replace('{query}', query).replace('{page}', str(page))
            )

            hits = response.json()['results'][0]['hits']

            if len(hits) == 0:
                break

            for hit in hits:
                nsuid = hit.get('nsuid')

                if not nsuid:
                    continue

                if nsuid in CACHE:
                    continue
                else:
                    CACHE.add(nsuid)

                yield nsuid, hit.get('slug')

            page += 1


def extract_game_data(system, slug):
    url = AMERICA[DATA].format(slug=slug)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = [tag.text for tag in soup.find_all('script') if 'window.game' in tag.text]

    if not len(scripts):
        return None

    data = {x[0]: x[1] for x in [line.strip().replace('",', '').split(': "') for line in scripts[0].split('\n') if ':' in line]}

    nsuid = data.get('nsuid')
    game_code = data.get('productCode')

    if len(nsuid) < 10 or len(game_code) < 7:
        return None

    title = data.get('title')\
        .replace('\\u002D', '-')\
        .replace('\\x22', '"') \
        .replace('\\x26', '&') \
        .replace('\\x27', "'")\
        .strip()

    game_id = get_game_id(nsuid=nsuid, game_id=game_code)

    game = Game(_id=game_id, system=system)
    game.titles[NA] = FIXES.get(title, title)
    game.nsuids[NA] = FIXES.get(nsuid, nsuid)
    game.categories = get_categories(data.get('genre', '').split(','))
    game.free_to_play = data.get('msrp') == '0.00'
    game.published_by_nintendo = data.get('publisher') == 'Nintendo'

    for country, details in COUNTRIES.items():
        if details[REGION] == NA and WEBSITE in details:
            game.websites[country] = details[WEBSITE].format(nsuid=nsuid)

    try:
        game.release_dates[NA] = datetime.strptime(
            soup.find('dd', {'itemprop': 'releaseDate'}).text.strip(),
            '%b %d, %Y'
        )
    except Exception as e:
        return None

    try:
        number_of_players = soup.find('dd', {'class': 'num-of-players'}).text.strip()
        game.number_of_players = int(re.sub('[^0-9]*', '', number_of_players))
    except:
        game.number_of_players = 0

    return game


def list_new_games(system, games_on_db):
    CACHE.clear()

    for nsuid, slug in fetch_games(system):
        if nsuid in games_on_db:
            continue

        game = extract_game_data(system, slug)

        if game:
            if game.id in ['3DS/AL8']:
                continue

            LOG.info(f'Found new game {game} {nsuid}')

            yield nsuid, game
        else:
            LOG.error(f'Failed to extract data for game with nsuid {nsuid}')
