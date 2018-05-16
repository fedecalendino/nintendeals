# Standard
from datetime import datetime
import re
import logging

# Dependencies
import requests

# Constants
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('nintendo.na')


REGION = REGIONS[NA_]
LIST_API = REGION[api_]


def get_deals(system, limit=100, offset=0):
    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][NA_], limit=limit, offset=offset))
    json = r.json()

    total = json['filter']['total']

    if total == 0:
        return {}

    games = {}

    for data in json['games']['game']:
        game_id = "{}-{}".format(system, data['game_code'][-5:])

        release_date = datetime.strptime(data['release_date'], '%b %d, %Y')

        number_of_players = re.sub('[^0-9]*', '', data['number_of_players'])

        categories = data['categories']['category']
        if type(categories) == str:
            categories = [categories]

        categories.sort()

        if 'nsuid' not in data:
            continue

        game = {
            id_: game_id,
            ids_: {
                NA_: data['nsuid']
            },
            title_: data['title'],
            system_: system,
            websites_: {},
            release_date_: release_date.strftime('%Y-%m-%d'),
            number_of_players_: int(number_of_players) if len(number_of_players) else 0,
            genres_: [cat.lower() for cat in categories]
        }

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == NA_:
                if websites_ in country_details:
                    if 'slug' in data:
                        game[websites_][country] = country_details[websites_].format(data['slug'])

        games[game_id] = game

    if total > limit + offset:
        games.update(get_deals(system, limit, offset + limit))

    return games


