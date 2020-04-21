import logging
from time import sleep

import dateutil.parser
import requests

from commons.classes import CountryPrice
from commons.classes import Sale
from commons.config import PRICE_API
from commons.keys import ES
from commons.keys import EU

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

            full_price = float(data['regular_price']['raw_value'])

            price = CountryPrice(
                country=country,
                currency=data['regular_price']['currency'],
                full_price=full_price
            )

            latest_sale = None

            if data.get('discount_price'):
                sale_price = float(data['discount_price']['raw_value'])

                latest_sale = Sale(
                    sale_price=sale_price,
                    discount=round(100 * (1 - (sale_price / full_price))),
                    start_date=dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None),
                    end_date=dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)
                )

            yield data.get('title_id'), price, latest_sale
        except Exception as e:
            LOG.info(f'Error: {country}/{data.get("title_id")} > {str(e)}')
            continue


def fetch_prices(country, nsuids):
    sleep(1)

    size = 50

    for index in range(0, int(len(nsuids) / size) + 1):
        chunk = nsuids[size * index:size * (index + 1)]

        LOG.info(f'Looking prices for {country}: {size * (index + 1)}/{len(nsuids)}')

        for nsuid, price, sale in _fetch_prices(country, chunk):
            yield nsuid, price, sale
