# Standard
import time
import logging

# Dependencies
import dateutil.parser
import requests

# Modules
from bot.db.mongo import PricesDatabase

# Constants
from bot.commons.config import *
from bot.commons.keys import *


LOG = logging.getLogger('🎮.🏷️ ')


PRICES_DB = PricesDatabase.instance()


def get_prices(country, ids):
    if country == EU_:
        country = ES_

    prices = {}

    response = requests.get(PRICE_API.format(country=country, ids=','.join(ids)))
    json = response.json()

    for data in json['prices']:
        try:
            if 'regular_price' not in data:
                continue

            if 'raw_value' not in data['regular_price']:
                continue

            price = {
                currency_: data['regular_price']['currency'],
                full_price_: float(data['regular_price']['raw_value'])
            }

            if 'discount_price' in data:
                price[sale_] = {}
                price[sale_][sale_price_] = float(data['discount_price']['raw_value'])

                price[sale_][start_date_] = dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None)
                price[sale_][end_date_] = dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)

                price[sale_][discount_] = round(
                    100 * (1 - (price[sale_][sale_price_] / price[full_price_]))
                )
            else:
                price[sale_] = None

            prices[data['title_id']] = price
        except Exception as e:
            LOG.info('Error: {}/{} > {}'.format(country, data['title_id'], str(e)))
            continue

    time.sleep(1)

    return prices


def fetch_prices():
    ids_by_country = {}

    for price in PRICES_DB.load_all():
        for country in price[countries_]:
            if country not in ids_by_country:
                ids_by_country[country] = []

            if price[id_].startswith('5001') or price[id_].startswith('7001'):
                ids_by_country[country].append(price[id_])

    for country, ids in ids_by_country.items():
        for index in range(0, int(len(ids)/50) + 1):
            LOG.info('Looking for prices from {} to {} for {}'.format(50 * index, 50 * (index + 1), country))

            segment = ids[50 * index:50 * (index + 1)]

            prices = get_prices(country, segment)

            for nsuid, data in prices.items():
                price = PRICES_DB.load(str(nsuid))

                if price[countries_][country] is None:
                    price[countries_][country] = {}

                price[countries_][country][currency_] = data[currency_]
                price[countries_][country][full_price_] = data[full_price_]

                if data[sale_] is not None:
                    LOG.info('Deal found for {} on {}'.format(nsuid, country))

                    deal = {
                        sale_price_: data[sale_][sale_price_],
                        start_date_: data[sale_][start_date_],
                        end_date_: data[sale_][end_date_],
                        discount_: data[sale_][discount_],
                    }

                    if sales_ not in price[countries_][country]:
                        price[countries_][country][sales_] = []
                        price[countries_][country][sales_].append(deal)
                    else:
                        current = price[countries_][country][sales_][-1]

                        if deal[end_date_] > current[end_date_]:
                            price[countries_][country][sales_].append(deal)

                PRICES_DB.save(price)

