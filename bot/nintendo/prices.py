import logging
from time import sleep

import dateutil.parser
import requests

from commons.config import PRICE_API
from commons.keys import CURRENCY
from commons.keys import DISCOUNT
from commons.keys import END_DATE
from commons.keys import ES
from commons.keys import EU
from commons.keys import FULL_PRICE
from commons.keys import SALE
from commons.keys import SALE_PRICE
from commons.keys import START_DATE


LOG = logging.getLogger('nintendo.prices')


def _fetch_prices(country, nsuids):
    if country == EU:
        country = ES

    response = requests.get(PRICE_API.format(country=country, ids=','.join(nsuids)))
    json = response.json()

    for data in json['prices']:
        try:
            if not data.get('regular_price', {}).get('raw_value'):
                continue

            price = {
                CURRENCY: data['regular_price']['currency'],
                FULL_PRICE: float(data['regular_price']['raw_value'])
            }

            if data.get('discount_price'):
                price[SALE] = {
                    SALE_PRICE: float(data['discount_price']['raw_value']),
                    START_DATE: dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None),
                    END_DATE: dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)
                }

                price[SALE][DISCOUNT] = round(100 * (1 - (price[SALE][SALE_PRICE] / price[FULL_PRICE])))
            else:
                price[SALE] = None

            yield data.get('title_id'), price
        except Exception as e:
            LOG.info('Error: {}/{} > {}'.format(country, data.get('title_id'), str(e)))
            continue


def fetch_prices(country, nsuids):
    sleep(1)

    size = 50

    for index in range(0, int(len(nsuids) / size) + 1):
        chunk = nsuids[size * index:size * (index + 1)]

        LOG.info('Looking prices for {}: {}/{}'.format(country, size * (index + 1), len(nsuids)))

        for nsuid, price in _fetch_prices(country, chunk):
            yield nsuid, price
