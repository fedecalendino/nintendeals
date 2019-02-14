import logging

from bot.nintendo import prices

from db.mongo import PricesDatabase

from commons.config import COUNTRIES
from commons.keys import CURRENCY
from commons.keys import DISCOUNT
from commons.keys import END_DATE
from commons.keys import FULL_PRICE
from commons.keys import ID
from commons.keys import LATEST_SALE
from commons.keys import SALE
from commons.keys import SALES
from commons.keys import START_DATE


LOG = logging.getLogger('jobs.prices')


def find_and_save_prices():
    prices_db = PricesDatabase()

    nsuids_by_country = {country: [] for country in COUNTRIES}

    for price in prices_db.load_all():
        for country in COUNTRIES:
            if country not in price:
                continue

            if len(price[ID]) < 10:
                continue

            nsuids_by_country[country].append(price[ID])

    for country, nsuids in nsuids_by_country.items():
        LOG.info('Looking prices for {}: {} in total'.format(country, len(nsuids)))

        for nsuid, price in prices.fetch_prices(country, nsuids):
            price_db = prices_db.load(str(nsuid))

            if not price_db[country]:
                price_db[country] = {}

            price_db[country][CURRENCY] = price[CURRENCY]
            price_db[country][FULL_PRICE] = price[FULL_PRICE]
            price_db[country][SALES] = price_db[country].get(SALES, [])

            sale = price.get(SALE)

            if sale:
                sale_db = price_db[country][SALES][-1] if len(price_db[country][SALES]) else None

                if sale_db:
                    if sale[START_DATE] > sale_db[END_DATE]:
                        price_db[country][SALES].append(sale)
                        LOG.info('New sale found for {} ({}%)'.format(nsuid, sale[DISCOUNT]))
                else:
                    price_db[country][SALES].append(sale)
                    LOG.info('New sale found for {} ({}%)'.format(nsuid, sale[DISCOUNT]))

            price_db[country][LATEST_SALE] = sale
            prices_db.save(price_db)


logging.basicConfig(level=logging.INFO)
find_and_save_prices()