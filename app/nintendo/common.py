# Standard
from datetime import datetime
import logging
import time

# Dependencies
import dateutil.parser
import requests

# Modules
from app.db.mongo import GamesDatabase
from app.commons.util import *
from app.metacritic import metacritic

# Constants
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('nintendo.common')


def get_price(country, id, title):
    now = datetime.utcnow().replace(tzinfo=None)

    if country == EU_:
        country = ES_

    try:
        r = requests.get(PRICE_API.format(country=country, id=id))
        data = r.json()

        data = data['prices'][0]

        price = {
            full_price_: float(data['regular_price']['raw_value']),
            currency_:  data['regular_price']['currency']
        }

        if 'discount_price' in data:
            price[sale_price_] = float(data['discount_price']['raw_value'])
            price[start_date_] = dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None)
            price[end_date_] = dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)

            price[discount_] = round(
                100 * (1 - (price[sale_price_] / price[full_price_]))
            )

            LOG.info("New sale found for {} on {}".format(title, country))
        else:
            price[sale_price_] = None
            price[discount_] = None
            price[start_date_] = None
            price[end_date_] = None

        price[last_update_] = now

        return price
    except Exception as e:
        return None


def find_prices_and_scores(games):
    now = datetime.utcnow().replace(tzinfo=None)

    updated_games = []

    for id, game in games.items():
        saved_game = GamesDatabase.instance().load(id)

        if saved_game is not None:
            saved_game[ids_] = merge(game[ids_], saved_game[ids_])
            saved_game[websites_] = merge(game[websites_], saved_game[websites_])

            game = saved_game
        else:
            if prices_ not in game:
                game[prices_] = {}

        if title_ in game:
            if 'Â®' in game[title_]:
                game[title_] = game[title_].replace('Â®', '®')

            title = game[title_]
        else:
            title = game[title_jp_]

        if saved_game is not None:
            LOG.info('Loaded {} from database'.format(title))
        else:
            LOG.info('Found new game: {}'.format(title))

        LOG.info("Fetching scores for {}".format(title))
        game = metacritic.find_scores(game)

        for country, country_details in COUNTRIES.items():
            if country not in game[prices_]:
                game[prices_][country] = []

            current = None

            if len(game[prices_][country]) > 0:
                current = game[prices_][country][-1]

                if (now - current[last_update_]).total_seconds() < UPDATE_FREQUENCY * 3/2:
                    continue

                if current[end_date_] is not None and current[end_date_] > now:
                    LOG.info("Sale for {} on {} still up".format(title, country))
                    continue

            region = country_details[region_]

            if region in game[ids_]:
                LOG.info("Fetching price for {} on {}".format(title, country))

                price = get_price(country, game[ids_][region], title)

                if price is not None:
                    if price[discount_] is None:
                        if current is not None:
                            current[last_update_] = now
                        else:
                            game[prices_][country].append(price)
                    else:
                        game[prices_][country].append(price)



        GamesDatabase.instance().save(game)
        updated_games.append(game)

        time.sleep(1)

    return updated_games
