import logging
from datetime import datetime

from bot.wishlist.constants import GAME_ADDED
from bot.wishlist.constants import GAME_REMOVED
from bot.wishlist.constants import INVALID_COUNTRIES
from bot.wishlist.constants import INVALID_COUNTRY
from bot.wishlist.constants import INVALID_GAME_ID
from bot.wishlist.constants import INVALID_WISHLISTED_GAME
from bot.wishlist.constants import NO_WISHLIST
from bot.wishlist.constants import WISHLIST_DELETED
from bot.wishlist.constants import WISHLIST_EMPTY
from bot.wishlist.constants import WISHLIST_FULL
from bot.wishlist.constants import WISHLIST_SHOWED
from bot.wishlist.generator import build_response
from commons.classes import Wishlist
from commons.classes import WishlistedGame
from commons.config import COUNTRIES
from db.mongo import GamesDatabase
from db.mongo import WishlistDatabase

LOG = logging.getLogger('wishlist')
LIMIT = 50


def add(message, game_id):
    now = datetime.utcnow()
    username = message.author.name

    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    game = games_db.load(game_id)

    if not game:
        return build_response(
            INVALID_GAME_ID.format(game_id),
            username
        )

    countries = sorted(message.body.split(' '))

    invalid_countries = [country for country in countries if country not in COUNTRIES]

    if len(invalid_countries) == 1:
        return build_response(
            INVALID_COUNTRY.format(invalid_countries),
            username
        )
    elif len(invalid_countries) > 1:
        return build_response(INVALID_COUNTRIES.format(
            invalid_countries),
            username
        )

    wishlist = wishlist_db.load(username)

    if not wishlist:
        wishlist = Wishlist(_id=username)

    if len(wishlist.games) > LIMIT:
        return build_response(
            WISHLIST_FULL.format(len(wishlist.games), LIMIT),
            username
        )

    wishlist.games[game_id] = WishlistedGame(
        _id=game_id,
        countries={country: now for country in countries}
    )

    wishlist_db.save(wishlist)

    LOG.info(f'{username} added {game.title} to the wishlist')

    return build_response(
        GAME_ADDED.format(game.title),
        username
    )


def remove(message, game_id):
    username = message.author.name

    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    game = games_db.load(game_id)

    if not game:
        return build_response(
            INVALID_GAME_ID.format(game_id),
            username
        )

    wishlist = wishlist_db.load(username)

    if not wishlist:
        return build_response(
            NO_WISHLIST,
            username
        )

    if game_id in wishlist.games:
        del wishlist.games[game_id]
        wishlist_db.save(wishlist)

        LOG.info(f'{username} removed {game.title} to the wishlist')

        return build_response(
            GAME_REMOVED.format(game.title),
            username
        )
    else:
        return build_response(
            INVALID_WISHLISTED_GAME.format(game.title),
            username
        )


def show(message, _):
    username = message.author.name

    wishlist_db = WishlistDatabase()
    wishlist = wishlist_db.load(username)

    if not wishlist:
        return build_response(
            NO_WISHLIST,
            username
        )

    if not len(wishlist.games):
        return build_response(
            WISHLIST_EMPTY,
            username
        )
    else:
        LOG.info(f'{username} asked for to the wishlist')

        return build_response(
            WISHLIST_SHOWED,
            username
        )


def delete(message, _):
    username = message.author.name

    wishlist_db = WishlistDatabase()
    wishlist = wishlist_db.load(username)

    if not wishlist:
        return build_response(
            NO_WISHLIST,
            username
        )

    wishlist_db.remove(username)

    LOG.info(f'{username} deleted the wishlist')

    return build_response(
        WISHLIST_DELETED,
        username
    )
