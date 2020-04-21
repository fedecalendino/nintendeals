import logging
from datetime import datetime
from datetime import timedelta

from bot.reddit import Reddit
from bot.wishlist import generator
from bot.wishlist.constants import GAMES_ON_SALE
from commons.config import COUNTRIES
from commons.keys import ID
from commons.keys import REGION
from db.mongo import WishlistDatabase
from db.util import get_games_on_sale

LOG = logging.getLogger('jobs.wishlist')


def notify_users():
    notified_users = 0

    reddit = Reddit()
    wishlist_db = WishlistDatabase()

    games, sales = get_games_on_sale()

    wishlists = {wishlist.id: wishlist for wishlist in wishlist_db.load_all(sort=[(ID, 1)])
                    if any([game_id for game_id in wishlist.games if game_id in games])}

    for username, wishlist in wishlists.items():
        sales_to_notify = []

        for game_id in wishlist.games:
            if game_id not in games:
                continue

            game = games[game_id]

            for country, last_update in wishlist.games[game_id].countries.items():
                if last_update > datetime.utcnow():
                    continue

                region = COUNTRIES[country][REGION]
                nsuid = game.nsuids[region]

                if nsuid not in sales:
                    continue

                price = sales[nsuid]
                country_price = price.prices[country]

                if not country_price:
                    LOG.error(f'{game_id} has no country price for {country}')
                    continue

                sale = country_price.active

                if not sale:
                    continue

                sales_to_notify.append((game, country_price, country, sale))
                wishlist.games[game_id].countries[country] = sale.end_date + timedelta(days=+2)

        if len(sales_to_notify):
            body = generator.generate_notification(sales_to_notify)
            content = generator.build_response(body, username)

            if len(content) > 9500:
                content = generator.build_response(body, username, include_wishlist=False)

            reddit.send(username, GAMES_ON_SALE, content)
            wishlist_db.save(wishlist)

            LOG.info(f'Notified {username} about {len(sales_to_notify)} sales')
            notified_users += 1

    return f'Notified users: {notified_users}'
