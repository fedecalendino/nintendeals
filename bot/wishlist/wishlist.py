from datetime import datetime
from datetime import timedelta

from bot.reddit import Reddit
from bot.wishlist import generator

from db.mongo import GamesDatabase
from db.mongo import WishlistDatabase
from db.util import get_games_on_sale
from db.util import get_latest_sale

from bot.wishlist.constants import GAME_ADDED
from bot.wishlist.constants import GAMES_ON_SALE
from bot.wishlist.constants import GAME_REMOVED
from bot.wishlist.constants import INVALID_COUNTRIES
from bot.wishlist.constants import INVALID_COUNTRY
from bot.wishlist.constants import INVALID_GAME_ID
from bot.wishlist.constants import INVALID_WISHLISTED_GAME
from bot.wishlist.constants import NO_WISHLIST
from bot.wishlist.constants import SEPARATOR
from bot.wishlist.constants import WISHLIST_DELETED
from bot.wishlist.constants import WISHLIST_EMPTY
from bot.wishlist.constants import WISHLIST_SHOWED
from bot.wishlist.constants import WL_ADD
from bot.wishlist.constants import WL_DELETE
from bot.wishlist.constants import WL_REMOVE
from bot.wishlist.constants import WL_SHOW

from commons.config import COUNTRIES
from commons.keys import END_DATE
from commons.keys import GAMES
from commons.keys import ID
from commons.keys import NAME
from commons.keys import NSUIDS
from commons.keys import REGION
from commons.keys import TITLE

import logging


LOG = logging.getLogger('wishlist')


def add(message, game_id):
    now = datetime.utcnow()

    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    game = games_db.load(game_id)

    if not game:
        return INVALID_GAME_ID.format(game_id)

    countries = sorted(message.body.split(' '))

    invalid_countries = [country for country in countries if country not in COUNTRIES]

    if len(invalid_countries) == 1:
        return INVALID_COUNTRY.format(invalid_countries)
    elif len(invalid_countries) > 1:
        return INVALID_COUNTRIES.format(invalid_countries)

    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        wishlist = {
            ID: message.author.name,
            GAMES: {}
        }

    wishlist[GAMES][game_id] = {country: now for country in countries}
    wishlist_db.save(wishlist)

    LOG.info(f'{message.author.name} added {game[NAME]} to the wishlist')

    return GAME_ADDED.format(game[TITLE])


def remove(message, game_id):
    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    game = games_db.load(game_id)

    if not game:
        return INVALID_GAME_ID.format(game_id)

    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        return NO_WISHLIST

    if game_id in wishlist.get(GAMES, {}):
        del wishlist[GAMES][game_id]
        wishlist_db.save(wishlist)

        LOG.info(f'{message.author.name} removed {game[NAME]} to the wishlist')

        return GAME_REMOVED.format(game[TITLE])
    else:
        return INVALID_WISHLISTED_GAME.format(game[NAME])


def show(message, _):
    wishlist_db = WishlistDatabase()
    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        return NO_WISHLIST

    if not len(wishlist.get(GAMES, {})):
        return WISHLIST_EMPTY
    else:
        LOG.info(f'{message.author.name} asked for to the wishlist')

        return WISHLIST_SHOWED


def delete(message, _):
    wishlist_db = WishlistDatabase()
    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        return NO_WISHLIST

    wishlist_db.remove(message.author.name)

    LOG.info(f'{message.author.name} deleted the wishlist')

    return WISHLIST_DELETED


def unknown(message, _):
    return None


COMMANDS = {
    WL_ADD: add,
    WL_REMOVE: remove,
    WL_SHOW: show,
    WL_DELETE: delete,
}


def check_inbox():
    reddit = Reddit()

    for message in reddit.inbox():
        subject = message.subject.upper()

        split = subject.split(SEPARATOR)

        command = COMMANDS.get(split[0], unknown)
        content = command(message, split[1] if len(split) > 1 else None)

        if not content:
            continue

        body = [
            generator.generate_header(message.author.name),
            '',
            '',
            content,
            '___',
            generator.build_wishlist(message.author.name),
            '___',
            generator.generate_footer()
        ]

        reddit.reply(message, '\n'.join(body))


def notify_users():
    reddit = Reddit()
    now = datetime.utcnow()
    wishlist_db = WishlistDatabase()

    games, sales = get_games_on_sale()

    wishlists = {wishlist[ID]: wishlist for wishlist in wishlist_db.load_all()
                    if any([game_id for game_id in wishlist[GAMES] if game_id in games])}

    for username, wishlist in wishlists.items():
        sales_to_notify = []

        for game_id in wishlist[GAMES]:
            if game_id not in games:
                continue

            game = games[game_id]
            print('')

            for country, last_update in {k: v for k, v in wishlist[GAMES][game_id].items()}.items():
                if last_update > now:
                    continue

                region = COUNTRIES[country][REGION]
                nsuid = game[NSUIDS][region]

                if nsuid not in sales:
                    continue

                price = sales[nsuid][country]
                sale = get_latest_sale(price)

                if not sale:
                    continue

                sales_to_notify.append((game, price, country, sale))
                wishlist[GAMES][game_id][country] = sale[END_DATE] + timedelta(days=1)

        if len(sales_to_notify):
            content = generator.generate_notification(sales_to_notify)
            reddit.send(username, GAMES_ON_SALE, content)
            wishlist_db.save(wishlist)

            LOG.info(f'Notified {username} about {len(sales_to_notify)} sales')

