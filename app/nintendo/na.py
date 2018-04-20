# Standard
from datetime import datetime
import logging

# Dependencies
import dateutil.parser
import requests

# Modules
from app.db.mongo import GamesDatabase

# Utils
from app.commons.util import format_float

# Constants
from app.commons.config import *
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

    for data in json['games']['game']:
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

                        LOG.info(' New deal for {} found in {}'.format(data['title'], country))

        GamesDatabase.instance().save(game)

    return games


def one_table_per_country(games):
    text = []

    text.append('')
    text.append('')
    text.append("# {} ({} deals)".format(NA_, len(games)))
    text.append('')

    for country, properties in REGION[countries_].items():
        text.append('##{} {}'.format(properties[flag_], properties[name_]))
        text.append('')

        text.append('Title | Expiration | Price | % | Players')
        text.append('--- | --- | --- | --- | --- ')

        # Get max full price for leading zeroes
        max_sale = "%.2f" % max(
            [
                game[countries_][country][prices_][-1][sale_price_]
                for game in games if len(game[countries_][country][prices_]) > 0
            ]
        )

        # Get max full price for leading zeroes
        max_full = "%.2f" % max(
            [
                game[countries_][country][prices_][-1][full_price_]
                for game in games if len(game[countries_][country][prices_]) > 0
            ]
        )

        for game in games:

            details = game[countries_][country]

            if len(details[prices_]) < 1:
                continue

            title = details[title_]

            if len(title) > 40:
                title = title[:35] + '…'

            if len(details[website_]) > 0:
                title = "[{}]({})".format(title, details[website_])

            currency = properties[currency_]

            price = details[prices_][-1]
            discount = price[discount_]

            max_discount = ''
            try:
                discounts = [
                    dtls[prices_][-1][discount_]
                    for (ctr, dtls) in game[countries_].items() if
                    dtls[prices_][-1][end_date_] > datetime.now()
                ]
                
                if any(d != discount for d in discounts):
                    if discount == max(discounts):
                        max_discount = EMOJI_MAX_DISCOUNT
            except:
                pass

            sale_price = format_float(price[sale_price_], len(max_sale))
            full_price = format_float(price[full_price_], len(max_full))

            time_left = price[end_date_] - datetime.utcnow()

            if time_left.days > 0:
                days = time_left.days
                time = "{}d".format(days)

                warning = EMOJI_EXP_TOMORROW if days < 2 else ''
            else:
                hours = round(time_left.seconds/60/60)
                time = "{}h".format(hours)

                warning = EMOJI_EXP_TODAY if hours < 24 else ''

            new = EMOJI_NEW if (datetime.now() - price[start_date_]).days < 2 else ''

            players = game[number_of_players_]

            if players is None:
                players = 'TBD'
            else:
                players = players \
                    .replace(' players', '') \
                    .replace('To be determined', '- tbd -')

            text.append(
                '{title} {new}{warning} | '
                '*{end_date} ({time_left})* | '
                '{currency} **{sale_price}** ~~{full_price}~~ | '
                '`{discount}%`{min_discount} | '
                '{players}'.format(
                    title=title, new=new, warning=warning,
                    end_date=price[end_date_].strftime("%B %d"), time_left=time,
                    currency=currency, sale_price=sale_price,full_price=full_price,
                    discount=discount, min_discount=max_discount,
                    players=players)
                )

        text.append('')

    return '\n'.join(text)
