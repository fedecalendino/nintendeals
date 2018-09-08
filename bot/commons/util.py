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
        return game[title_]
    else:
        return game[title_jp_]


def get_relevance_score(game):
    from bot.db.mongo import PricesDatabase

    PRICES_DB = PricesDatabase.instance()

    countries = {}

    total_sales = 0
    total_countries = 0
    days_on_sale = 0
    days_on_fullprice = 0

    now = datetime.now()

    for id in game[ids_].values():
        for country, prices in PRICES_DB.load(id)[countries_].items():
            countries[country] = prices

            total_countries += 1

            if prices is None or sales_ not in prices:
                continue

            for index in range(len(prices[sales_])):
                total_sales += 1

                sale = prices[sales_][index]

                days_on_sale += (sale[end_date_] - sale[start_date_]).days

                if index + 1 < len(prices[sales_]):
                    next_sale = prices[sales_][index + 1]
                    days_on_fullprice += (next_sale[start_date_] - sale[end_date_]).days

    try:
        game_release = datetime.strptime(game[release_date_], '%Y-%m-%d')
    except:
        game_release = now

    days_since_release = (now - game_release).days + 1

    return days_on_fullprice * days_on_sale / days_since_release
