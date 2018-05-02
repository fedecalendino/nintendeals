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


def get_price(country, id, title=None):

    try:
        r = requests.get(PRICE_API.format(country=country, id=id))
        data = r.json()

        data = data['prices'][0]

        if title is None:
            LOG.info(' Pricing found {} on {}'.format(id, country))
        else:
            LOG.info(' Pricing found for {} on {}'.format(title, country))

        price = {
            full_price_: float(data['regular_price']['raw_value']),
            currency_:  data['discount_price']['currency']
        }

        if 'discount_price' in data:
            price[sale_price_] = float(data['discount_price']['raw_value'])
            price[start_date_] = dateutil.parser.parse(data['discount_price']['start_datetime']).replace(tzinfo=None)
            price[end_date_] = dateutil.parser.parse(data['discount_price']['end_datetime']).replace(tzinfo=None)

            price[discount_] = round(
                100 * (1 - (price[sale_price_] / price[full_price_]))
            )
        else:
            price[sale_price_] = None
            price[discount_] = None
            price[start_date_] = None
            price[end_date_] = None

        return price
    except:
        return None


def find_prices(games):
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

        game = metacritic.find_scores(game)

        for region, id in game[ids_].items():
            for country, details in REGIONS[region][countries_].items():
                if country not in game[prices_]:
                    game[prices_][country] = []

                if len(game[prices_][country]) > 0:
                    current = game[prices_][country][-1]

                    if current[end_date_] > datetime.now():
                        continue

                if title_ in game:
                    title = game[title_]
                else:
                    title = game[title_jp_]

                price = get_price(details[key_], id, title)

                if price is not None:
                    game[prices_][country].append(price)

        GamesDatabase.instance().save(game)
        updated_games.append(game)

        time.sleep(1)

    return updated_games


def make_post(games, region):
    text = []

    text.append('')

    for country, properties in REGIONS[region][countries_].items():

        if len([game for game in games if country in game[prices_]]) == 0:
            return None

        deal_count = 0
        max_sale = 0
        max_full = 0

        for game in games:
            if country in game[prices_] and len(game[prices_][country]) > 0:
                sale = game[prices_][country][-1][sale_price_]
                full = game[prices_][country][-1][full_price_]

                if max_sale < sale:
                    max_sale = sale

                if max_full < full:
                    max_full = full

                deal_count += 1

        # Get max prices for leading zeroes
        max_sale = "%.2f" % max_sale
        max_full = "%.2f" % max_full

        text.append('##{} {} ({} deals)'.format(properties[flag_], properties[name_], deal_count))
        text.append('')

        text.append('Title | Expiration | Price | % | Players | Score')
        text.append('--- | --- | --- | --- | --- | ---')

        for game in games:
            if country not in game[prices_]:
                continue

            details = game[prices_][country]

            if len(details) < 1:
                continue

            if title_ in game:
                title = game[title_]

                if len(title) > 30:
                    title = title[:29] + '…'
            else:
                title = game[title_jp_]

                if len(title) > 20:
                    title = title[:19] + '…'

            if country in game[websites_]:
                title = "[{}]({})".format(title, game[websites_][country])

            price = details[-1]

            if price[end_date_] < datetime.now():
                continue

            currency = price[currency_]
            sale_price = format_float(price[sale_price_], len(max_sale))
            full_price = format_float(price[full_price_], 0)
            discount = price[discount_]

            best_discount = discount
            all_equals = True

            for _, prices in game[prices_].items():
                if len(prices) > 0 and prices[-1][end_date_] > datetime.now():

                    if prices[-1][discount_] > best_discount:
                        best_discount = prices[-1][discount_]

                    if prices[-1][discount_] != best_discount:
                        all_equals = False

            if not all_equals and best_discount == discount:
                best_discount = EMOJI_MAX_DISCOUNT
            else:
                best_discount = ''

            time_left = price[end_date_] - datetime.now()

            if time_left.days > 0:
                days = time_left.days
                time = "{}d".format(days)

                warning = EMOJI_EXP_TOMORROW if days < 2 else ''
            else:
                hours = round(time_left.seconds / 60 / 60)
                time = "{}h".format(hours)

                warning = EMOJI_EXP_TODAY if hours <= 24 else ''

            new = EMOJI_NEW if (datetime.now() - price[start_date_]).days < 2 else ''

            players = game[number_of_players_]

            if players is None or players == 0:
                players = '- tbd -'
            elif players == 1:
                players = '1 player'
            elif players == 2:
                players = '2 players'
            else:
                players = 'up to {}'.format(players)

            score = ''

            if scores_ in game and len(game[scores_]) > 0:
                if metascore_ in game[scores_] and game[scores_][metascore_] is not None:
                    score = "{} `{}`".format(EMOJI_METACRITIC, int(game[scores_][metascore_]))
                elif userscore_ in game[scores_] and game[scores_][userscore_] is not None:
                    score = "{} `{}`".format(EMOJI_USER, "%.1f" % game[scores_][userscore_])


            text.append(
                '{title} {new}{warning} | '
                '*{end_date} ({time_left})* | '
                '{currency} **{sale_price}** ~~{full_price}~~ | '
                '`{discount}%` {best_discount}| '
                '{players} | {score}'.format(
                    title=title, new=new, warning=warning,
                    end_date=price[end_date_].strftime("%b %d"), time_left=time,
                    currency=currency, sale_price=sale_price, full_price=full_price,
                    discount=discount, best_discount=best_discount, players=players,
                    score=score)
            )

            deal_count += 1

        text.append('')

    return '\n'.join(text)


def make_unified_post(games):
    regions = []
    text = []

    for region in [NA_, EU_, JP_]:
        post = make_post(games, region)

        if post is not None:
            regions.append(region)
            text.append(post)

    return '\n'.join(text), regions