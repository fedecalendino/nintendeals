# Standard
from datetime import timedelta
from datetime import datetime
import logging

# Modules
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


def generate_message(sales, disable_urls=False):
    text = []
    text.append('')
    text.append('###Wishlisted games on sale')
    text.append('')

    text.append('Title | Expiration | Price | % ')
    text.append('--- | --- | --- | --- ')

    for sale in sales:
        country = sale[country_]
        country_details = COUNTRIES[country]

        game = sale[game_]
        price = sale[prices_]
        current_sale = sale[sale_]

        currency = country_details[currency_code_]
        sale_price = format_float(current_sale[sale_price_], 0)
        full_price = format_float(price[full_price_], 0)
        discount = current_sale[discount_]

        title = get_title(game)

        if not disable_urls:
            if websites_ in game and country in game[websites_]:
                title = '[{}]({})'.format(title, game[websites_][country].replace('https://www.', '//'))

        # Creating row
        text.append(
            '{title}|*{end_date}*|{flag} **{currency} {sale_price}** ~~{full_price}~~|`%{discount}`'.format(
                title=title, end_date=current_sale[end_date_].strftime("%b %d"), flag=country_details[flag_],
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
                try:
                    nsuid = game[ids_][COUNTRIES[country][region_]]
                except:
                    continue

                price = PRICES_DB.load(nsuid)[countries_][country]

                if price is None:
                    LOG.info('Price not found: {} {} {}'.format(nsuid, country, username))
                    continue

                if sales_ not in price:
                    continue

                sale = price[sales_][-1]

                if sale[discount_] < 1:
                    continue

                if sale[end_date_] < datetime.now():
                    continue

                sales_to_notify.append(
                    {
                        game_: game,
                        country_: country,
                        prices_: price,
                        sale_: sale
                    }
                )

                wishlist[games_][game_id][last_update_] = sale[end_date_] + timedelta(hours=1)

        content = generate_message(sales_to_notify)

        if len(content) > 10000:
            content = generate_message(sales_to_notify, disable_urls=True)

        if len(sales_to_notify) != 0:
            LOG.info('Sending notification to {}: {} deals found.'.format(username, len(sales_to_notify)))

            WISHLIST_DB.save(wishlist)
            Reddit.instance().send(username, 'New deals for your wishlisted games!', content)
