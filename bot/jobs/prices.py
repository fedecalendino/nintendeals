import logging

from bot.nintendo import prices

from db.mongo import PricesDatabase

from commons.config import COUNTRIES


LOG = logging.getLogger('jobs.prices')


def update_prices():
    deals_found = 0

    prices_db = PricesDatabase()

    loaded_prices = {}
    nsuids_by_country = {country: [] for country in COUNTRIES}

    for price in prices_db.load_all():
        for country in COUNTRIES:
            if country not in price.prices:
                continue

            if len(price.id) < 10:
                continue

            loaded_prices[price.id] = price
            nsuids_by_country[country].append(price.id)

    for country, nsuids in nsuids_by_country.items():
        LOG.info('Looking prices for {}: {} in total'.format(country, len(nsuids)))

        for nsuid, country_price, sale in prices.fetch_prices(country, nsuids):
            save = False

            nsuid = str(nsuid)
            price = loaded_prices.get(nsuid)

            if not price.prices[country]:
                price.prices[country] = country_price
                save = True

            country_price = price.prices[country]

            if sale:
                sale_db = country_price.latest_sale

                if sale_db:
                    if sale.start_date > sale_db.end_date:
                        country_price.sales.append(sale)
                        price.prices[country].latest_sale = sale

                        save = True
                        LOG.info('New sale found for {} ({}%)'.format(nsuid, sale.discount))
                        deals_found += 1
                else:
                    country_price.sales.append(sale)
                    price.prices[country].latest_sale = sale

                    save = True
                    LOG.info('New sale found for {} ({}%)'.format(nsuid, sale.discount))
                    deals_found += 1

            if save:
                prices_db.save(price)

    return f'Deals found: {deals_found}'
