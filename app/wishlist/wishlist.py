# Standard
from datetime import timedelta
from datetime import datetime
import logging

# Modules
from app.db.mongo import GamesDatabase
from app.db.mongo import PricesDatabase
from app.db.mongo import RedditDatabase
from app.db.mongo import WishlistDatabase

from app.reddit.reddit import Reddit

# Statics
from app.commons.config import *
from app.commons.keys import *
from app.commons.util import *


LOG = logging.getLogger('wishlist')


GAMES_DB = GamesDatabase.instance()
PRICES_DB = PricesDatabase.instance()
REDDIT_DB = RedditDatabase.instance()
WISHLIST_DB = WishlistDatabase.instance()


def generate_message(sales):
    text = []
    text.append('')
    text.append('###Wishlisted games on sale')
    text.append('')

    text.append('Title | Expiration | Price | % ')
    text.append('--- | --- | --- | --- ')

    for sale in sales:
        country_details = COUNTRIES[sale[country_]]
        price = sale[prices_]
        current_sale = sale[sale_]

        currency = country_details[currency_]
        sale_price = format_float(current_sale[sale_price_], country_details[digits_])
        full_price = format_float(price[full_price_], 0)
        discount = current_sale[discount_]

        # Creating row
        text.append(
            '{title}|*{end_date}*|{flag} **{currency}{sale_price}** ~~{full_price}~~|`%{discount}`'.format(
                title=sale[title_], end_date=current_sale[end_date_].strftime("%b %d"), flag=country_details[flag_],
                currency=currency, sale_price=sale_price, full_price=full_price, discount=discount)
        )

    return '\n'.join(text)


def notify():
    for wishlist in WISHLIST_DB.load_all():

        username = wishlist[id_]

        sales_to_notify = []

        for game_id, wishlist_details in wishlist[games_].items():
            game = GAMES_DB.load(game_id)

            if wishlist_details[last_update_] > datetime.now():
                continue

            for country in wishlist_details[countries_]:
                nsuid = game[ids_][COUNTRIES[country][region_]]

                price = PRICES_DB.load(nsuid)[countries_][country]

                if price is None:
                    print('Price not found: {} {} {}'.format(nsuid, country, username))
                    continue

                if sales_ not in price:
                    continue

                sale = price[sales_][-1]

                if sale[end_date_] < datetime.now():
                    continue

                if title_ in game:
                    title = game[title_]
                else:
                    title = game[title_jp_]

                sales_to_notify.append({title_: title, country_: country, prices_: price, sale_: sale})

                wishlist[games_][game_id][last_update_] = sale[end_date_] + timedelta(days=1)

        content = generate_message(sales_to_notify)

        if len(sales_to_notify) != 0:
            LOG.info('Sending notification to {}: {} deals found.'.format(username, len(sales_to_notify)))

            WISHLIST_DB.save(wishlist)
            Reddit.instance().send(username, 'New deals for games in your wishlist!', content)
