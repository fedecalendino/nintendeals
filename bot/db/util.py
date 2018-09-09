from datetime import datetime

from bot.commons.keys import *

from bot.db.mongo import GamesDatabase
from bot.db.mongo import PricesDatabase


GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()


def get_game_prices(game):
    return PRICES_DB.load_all(
        filter={
            id_: {
                '$in': list(game[ids_].values())
            }
        }
    )


def fill_game(game):
    game[final_title_] = (game[title_] if title_ in game else game[title_jp_])\
        .replace('\'', '')\
        .replace('’', '')\
        .title()

    game[prices_] = {}

    for region in get_game_prices(game):
        for country, details in region[countries_].items():
            if details is None:
                continue

            if sales_ not in details:
                continue

            if len(details[sales_]) == 0:
                continue

            game[prices_][country] = details

    return game


def get_relevance_score(game):
    total_sales = 0
    total_countries = 0

    days_on_sale = 0
    first_sale_start_date = None

    now = datetime.now()

    for country, details in game[prices_].items():
        if sales_ not in details:
            continue

        sales = details[sales_]

        total_countries += 1
        total_sales += len(sales)

        for sale in sales:
            days_on_sale += (sale[end_date_] - sale[start_date_]).days

            if first_sale_start_date is None:
                first_sale_start_date = sale[start_date_]
            elif sale[start_date_] < first_sale_start_date:
                first_sale_start_date = sale[start_date_]

    if total_countries == 0:
        return 0

    if days_on_sale == 0 or first_sale_start_date is None:  # never on sale
        return 0

    days_on_sale /= total_countries
    days_since_first_sale = (now - first_sale_start_date).days

    return days_since_first_sale * days_on_sale


def load_all_games(filter={}, on_sale_only=False, add_relevance=False):
    now = datetime.now()

    games = []

    for game in GAMES_DB.load_all({}):
        if on_sale_only:
            game = fill_game(game)

            on_sale = False

            for country, details in game[prices_].items():
                if len(details[sales_]) == 0:
                    continue

                last_sale = details[sales_][-1]

                if last_sale[discount_] < 1:
                    continue

                if last_sale[start_date_] < now < last_sale[end_date_]:
                    on_sale = True
                    break

            if on_sale:
                if add_relevance:
                    game[relevance_] = get_relevance_score(game)

                games.append(game)
        else:
            games.append(game)

    return sorted(games, key=lambda g: g[final_title_])
