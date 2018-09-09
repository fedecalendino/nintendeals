# Standard
from datetime import datetime
from datetime import timedelta
import logging

# Modules
from bot.db.util import load_all_games
from bot.db.mongo import GamesDatabase
from bot.db.mongo import PricesDatabase
from bot.db.mongo import RedditDatabase
from bot.db.mongo import WishlistDatabase

from bot.reddit.reddit import Reddit

# Statics
from bot.commons.config import *
from bot.commons.keys import *
from bot.commons.util import *


LOG = logging.getLogger('⭐')


GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()
REDDIT_DB = RedditDatabase.instance()
WISHLIST_DB = WishlistDatabase.instance()


def generate_message(notification, disable_urls=False):
    text = []
    text.append('')
    text.append('###Wishlisted games on sale')
    text.append('')

    text.append('Title | Expiration | Price | % ')
    text.append('--- | --- | --- | --- ')

    for game_id, details in notification.items():
        title = details[title_]

        for country, sale in details[countries_].items():
            country_details = COUNTRIES[country]

            currency = country_details[currency_code_]
            sale_price = format_float(sale[sale_price_], 0)
            full_price = format_float(sale[full_price_], 0)
            discount = sale[discount_]

            if not disable_urls:
                if websites_ in details:
                    if country in details[websites_]:
                        title = '[{}]({})'.format(title, details[websites_][country].replace('https://www.', '//'))

            # Creating row
            text.append(
                '{title}|*{end_date}*|{flag} **{currency} {sale_price}** ~~{full_price}~~|`%{discount}`'.format(
                    title=title, end_date=sale[end_date_].strftime("%b %d"), flag=country_details[flag_],
                    currency=currency, sale_price=sale_price, full_price=full_price, discount=discount)
            )

    return '\n'.join(text)


def notify():
    now = datetime.now()

    notifications = {}

    for game in load_all_games(filter={system_: SWITCH_}, on_sale_only=True):
        game_id = game[id_]

        users = WISHLIST_DB.load_all(
            filter={'games.{}'.format(game_id): {'$exists': True}}
        )

        if len(users) == 0:
            continue

        for user in users:
            if user[games_][game_id][last_update_] > now:
                continue

            username = user[id_]

            if username not in notifications:
                notifications[username] = {}

            notifications[username][game_id] = {
                title_: game[final_title_],
                websites_: game[websites_],
                countries_: {}
            }

            for country, details in game[prices_].items():
                last_sale = details[sales_][-1]

                if country in user[games_][game_id][countries_]:
                    notifications[username][game_id][countries_][country] = last_sale
                    notifications[username][game_id][countries_][country][full_price_] = details[full_price_]

                    user[games_][game_id][last_update_] = last_sale[end_date_] + timedelta(hours=1)
                    WISHLIST_DB.save(user)

    for username, notification in notifications.items():
        content = generate_message(notification)

        if len(content) > 10000:
            content = generate_message(notification, disable_urls=True)

        LOG.info('Sending notification to {}'.format(username))
        Reddit.instance().send(username, 'New deals for your wishlisted games!', content)
