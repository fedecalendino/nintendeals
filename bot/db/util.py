from datetime import datetime
from datetime import timedelta

from bot.commons.keys import *
from bot.commons.util import get_title

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


def fill_game(game, exclude_prices=False):
    game[final_title_] = get_title(game)

    game[prices_] = {}

    if exclude_prices:
        return game

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
    total_countries = 0

    time_span = 120

    now = datetime.now()
    start = now - timedelta(days=time_span)

    days_on_sale = 0

    for country, details in game[prices_].items():
        if sales_ not in details:
            continue

        counted_country = False

        sales = details[sales_]

        for sale in sales:
            start_date = sale[start_date_]
            end_date = sale[end_date_]

            if end_date < start:
                continue

            if start_date < start:
                start_date = start

            if not counted_country:
                total_countries += 1
                counted_country = True

            if end_date > now:
                days_on_sale += (now - start_date).days
            else:
                days_on_sale += (end_date - start_date).days

    if total_countries == 0:
        return 10

    days_on_sale /= total_countries

    return days_on_sale if days_on_sale <= time_span/5 else 0


def load_all_games(filter={}, exclude_prices=False, on_sale_only=False, add_relevance=False):
    now = datetime.now()

    games = []

    for game in GAMES_DB.load_all(filter):
        game = fill_game(game, exclude_prices)

        if on_sale_only:
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
