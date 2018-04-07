# Standard
from datetime import datetime
import logging

# Dependencies
import dateutil.parser
import requests

# Modules
from app.db.mongo import GamesDatabase

# Constants
from app.commons.config import REGIONS
from app.commons.keys import *


LOG = logging.getLogger('nintendo.na')


REGION = REGIONS[NA_]

LIST_API = REGION[api_][list_api_]
PRICE_API = REGION[api_][price_api_]


def get_price(country, id, title):
    LOG.info(' Fetching price for {}'.format(title))

    r = requests.get(PRICE_API.format(country, id))
    data = r.json()

    data = data['prices'][0]

    try:
        price = {
            full_price_: float(data['regular_price']['raw_value'])
        }

        if 'discount_price' in data:
            price[sale_price_] = float(data['discount_price']['raw_value'])
            price[start_date_] = dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None)
            price[end_date_] = dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)

            price[discount_] = round(
                100 * (1 - (price[sale_price_] / price[full_price_]))
            )
        else:
            price[sale_price_] = None
            price[discount_] = None
            price[start_date_] = None
            price[end_date_] = None

        return price
    except:
        return None


def get_games(system, limit=200, offset=0, deals_only=True):
    r = requests.get(LIST_API.format(system, limit, offset, '&sale=true' if deals_only else ''))
    json = r.json()

    games = []
    added_games = []

    for data in json['games']['game']:
        added = False

        game_id = data['game_code'][-5:]

        game = GamesDatabase.instance().load(game_id)

        if game is None:
            categories = data['categories']['category']

            if type(categories) == str:
                categories = [categories]

            game = {
                id_: game_id,
                system_: data['system'],
                release_date_: data['release_date'],
                number_of_players_: data['number_of_players'],
                genres_: categories
            }

            added = True
            LOG.info(' {} found'.format(data['title']))

        games.append(game)

        if countries_ not in game:
            game[countries_] = {}

        for country, properties in REGION[countries_].items():
            if country not in game[countries_]:
                game[countries_][country] = {
                    region_: NA_,
                    title_: data['title'],
                    website_: properties[website_].format(data['slug']) if 'slug' in data else '',
                    prices_: []
                }

        if 'sale_price' in data:
            for country in REGION[countries_]:
                prices = game[countries_][country][prices_]

                if len(prices) == 0 or prices[-1][end_date_] < datetime.now():
                    price = get_price(country, data['nsuid'], data['title'])

                    if price is not None:
                        prices.append(price)
                        added = True

                        LOG.info(' New deal for {} found'.format(data['title']))

        GamesDatabase.instance().save(game)

        if added:
            added_games.append(data['title'])

    return games, added_games


def make_post(games):
    text = []

    text.append('')
    text.append('')
    text.append("# {} ({} deals)".format(NA_, len(games)))
    text.append('')
    text.append(
        'Title | {} {} | {} {} | {} {} | Ends in'.format(
            REGION[countries_][US_][flag_], US_,
            REGION[countries_][CA_][flag_], CA_,
            REGION[countries_][MX_][flag_], MX_
        )
    )

    text.append('----- | ---- | --- | ---- | ----')

    for game in games:

        title_columns = []
        price_columns = []
        expiration_columns = []

        for country, details in game[countries_].items():

            title = details[title_]

            if len(title) >= 35:
                title = title[:32] + "..."

            title_columns.append(title)

            if len(details[prices_]) < 1:
                continue

            price = details[prices_][-1]

            currency = REGION[countries_][country][currency_]
            sale_price = "%.2f" % price[sale_price_]
            url = details[website_]

            if len(url) == 0:
                price_columns.append('`{}%` {} **{}**'.format(price[discount_], currency, sale_price))
            else:
                price_columns.append('`{}%` [{} **{}**]({})'.format(price[discount_], currency, sale_price, url))

            time_left = price[end_date_] - datetime.utcnow()

            if time_left.days > 0:
                time_left = str(time_left.days) + " days"
            else:
                time_left = round(time_left.days * 24 + time_left.seconds / 60 / 60)
                time_left = str(time_left) + " hours"

            expiration_columns.append(time_left)

        if len(price_columns) < 3:
            for i in range(len(price_columns), 3):
                price_columns.append(' ')

        text.append('{} | {} | {} '.format(
            title_columns[0],
            "|".join(price_columns),
            expiration_columns[0]
        ))

    return '\n'.join(text)
