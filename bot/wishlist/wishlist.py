import logging
from datetime import datetime

from db.mongo import GamesDatabase
from db.mongo import WishlistDatabase

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

from commons.classes import Wishlist
from commons.classes import WishlistedGame

from commons.config import COUNTRIES


LOG = logging.getLogger('wishlist')
LIMIT = 50


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
        wishlist = Wishlist(_id=message.author.name)

    if len(wishlist.games) > LIMIT:
        return WISHLIST_FULL.format(len(wishlist.games), LIMIT)

    wishlist.games[game_id] = WishlistedGame(
        _id=game_id,
        countries={country: now for country in countries}
    )

    wishlist_db.save(wishlist)

    LOG.info(f'{message.author.name} added {game.title} to the wishlist')

    return GAME_ADDED.format(game.title)


def remove(message, game_id):
    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    game = games_db.load(game_id)

    if not game:
        return INVALID_GAME_ID.format(game_id)

    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        return NO_WISHLIST

    if game_id in wishlist.games:
        del wishlist.games[game_id]
        wishlist_db.save(wishlist)

        LOG.info(f'{message.author.name} removed {game.title} to the wishlist')

        return GAME_REMOVED.format(game.title)
    else:
        return INVALID_WISHLISTED_GAME.format(game.title)


def show(message, _):
    wishlist_db = WishlistDatabase()
    wishlist = wishlist_db.load(message.author.name)

    if not wishlist:
        return NO_WISHLIST

    if not len(wishlist.games):
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
