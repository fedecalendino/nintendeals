# Standard
import logging

# Dependencies
import requests

# Constants
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('nintendo.eu')


REGION = REGIONS[EU_]
LIST_API = REGION[api_]


def get_deals(system, start=0):
    r = requests.get(LIST_API.format(system=SYSTEMS[system][system_][EU_], start=start))
    json = r.json()

    total = json['response']['numFound']

    if total == 0:
        return {}

    games = {}

    for data in json['response']['docs']:
        game_id = "{}-{}".format(system, data['product_code_txt'][0][-5:])

        categories = [cat.lower() for cat in data['game_categories_txt']]
        categories.sort()

        game = {
            id_: game_id,
            ids_: {
                EU_: data['nsuid_txt'][0]
            },
            title_: data['title'],
            websites_: {},
            system_: system,
            release_date_: data['dates_released_dts'][0][:10],
            number_of_players_: data['players_to'],
            genres_: categories
        }

        for country, country_details in COUNTRIES.items():
            if country_details[region_] == EU_:
                if websites_ in country_details:
                    game[websites_][country] = country_details[websites_].format(data['url'].rsplit('/', 1)[-1])

        games[game_id] = game

    if total > start + 10:
        games.update(get_deals(system, start + 10))

    return games
