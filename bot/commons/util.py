from datetime import datetime
from bot.commons.keys import *


def format_float(value, total_digits=0):
    value = '%.2f' % value

    if total_digits == 0:
        return value
    else:
        return '0' * (total_digits - len(value)) + value


def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def get_title(game):
    if title_ in game:
        title = game[title_]
    else:
        title = game[title_jp_]

    return title.replace('\'', '').replace('’', '').title()


def get_relevance_score(game):
    from bot.db.mongo import PricesDatabase
    PRICES_DB = PricesDatabase.instance()

    countries = {}

    total_sales = 0
    total_countries = 0
    days_on_sale = 0
    first_sale_start_date = None

    now = datetime.now()

    for id in game[ids_].values():
        for country, prices in PRICES_DB.load(id)[countries_].items():
            countries[country] = prices

            if prices is None or sales_ not in prices:
                continue

            total_countries += 1

            for index in range(len(prices[sales_])):
                total_sales += 1

                sale = prices[sales_][index]
                days_on_sale += (sale[end_date_] - sale[start_date_]).days

                if first_sale_start_date is None:
                    first_sale_start_date = sale[start_date_]

    if total_countries == 0:
        return 0

    if days_on_sale == 0 or first_sale_start_date is None:  # never on sale
        return 0

    days_on_sale /= total_countries
    days_since_first_sale = (now - first_sale_start_date).days

    return days_since_first_sale * days_on_sale
