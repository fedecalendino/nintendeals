import logging

from bot import metacritic

from db.mongo import GamesDatabase
from db.mongo import PricesDatabase
from db.mongo import WishlistDatabase

from bot.nintendo import eu
from bot.nintendo import jp
from bot.nintendo import na

from commons.classes import Game
from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS
from commons.emoji import NINTENDO
from commons.keys import CATEGORIES
from commons.keys import DB
from commons.keys import EU
from commons.keys import GAME_ID
from commons.keys import GAMES
from commons.keys import ID
from commons.keys import JP
from commons.keys import NA
from commons.keys import NSUIDS
from commons.keys import NUMBER_OF_PLAYERS
from commons.keys import PUBLISHED_BY_NINTENDO
from commons.keys import REGION
from commons.keys import RELEASE_DATE
from commons.keys import SCORES
from commons.keys import SYSTEM
from commons.keys import TITLE
from commons.keys import TITLE_EN
from commons.keys import TITLE_JP
from commons.keys import WEBSITES
from commons.keys import WISHLISTED


ENABLE_METACRITIC = False

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('jobs.games')


def get_wishlisted_count():
    wishlist_db = WishlistDatabase()

    counts = {}

    for wishlist in wishlist_db.load_all():
        for game_id in wishlist.get(GAMES, {}):
            counts[game_id] = counts.get(game_id, 0) + 1

    return counts


def add(games, key, game):
    game_id = game[ID]

    if games.get(game_id) is None:
        games[game_id] = {}

    games[game_id][key] = game


def merge_game(game_id, game, system):
    final = Game.create(game_id, system)

    for region in REGIONS:
        regional = game.get(region, {})

        final[NSUIDS][region] = regional.get(NSUIDS, {}).get(region)

        if not final.get(TITLE_JP):
            final[TITLE_JP] = regional.get(TITLE_JP)

        if not final.get(TITLE_EN):
            final[TITLE_EN] = regional.get(TITLE_EN)

        if not final.get(RELEASE_DATE):
            final[RELEASE_DATE] = regional.get(RELEASE_DATE)

        final[CATEGORIES] += regional.get(CATEGORIES, [])

        final[NUMBER_OF_PLAYERS] = max([
            final.get(NUMBER_OF_PLAYERS, 0),
            regional.get(NUMBER_OF_PLAYERS, 0)
        ])

        final[PUBLISHED_BY_NINTENDO] = any([
            final.get(PUBLISHED_BY_NINTENDO, False),
            regional.get(PUBLISHED_BY_NINTENDO, False)
        ])

        for country, website in regional.get(WEBSITES, {}).items():
            if website:
                final[WEBSITES][country] = website

    if final.get(TITLE_EN):
        final[TITLE] = final[TITLE_EN]
    else:
        final[TITLE] = final[TITLE_JP].title()

    final[TITLE] = final[TITLE].replace('#', '').strip()

    if final.get(PUBLISHED_BY_NINTENDO):
        final[TITLE] = ' {} {}'.format(NINTENDO, final[TITLE])

    final[CATEGORIES] = sorted(list(set(final.get(CATEGORIES, []))))

    if ENABLE_METACRITIC and final.get(TITLE_EN):
       final[SCORES] = metacritic.get_scores(system, final.get(TITLE_EN), game.get(DB, {}).get(SCORES))

    return final


def find_and_save_games(system, wishlisted_count=None):
    games_db = GamesDatabase()
    prices_db = PricesDatabase()

    games = {}

    for game in games_db.load_all(filter={SYSTEM: system}):
        add(games, DB, game)

    for game in eu.list_games(system):
        add(games, EU, game)

    for game in jp.list_games(system):
        add(games, JP, game)

    for game in na.list_games(system):
        add(games, NA, game)

    prices = {price[ID]: price for price in prices_db.load_all()}

    for game_id, game in games.items():
        final = merge_game(game_id, game, system)

        if wishlisted_count:
            final[WISHLISTED] = wishlisted_count.get(game_id, 0)

        GamesDatabase().save(final)

        for region, nsuid in final[NSUIDS].items():
            if not nsuid:
                continue

            save = False

            price = prices.get(nsuid)

            if price is None:
                save = True
                price = {
                    ID: nsuid,
                    GAME_ID: final[ID],
                    SYSTEM: system
                }

            for country, details in COUNTRIES.items():
                if details[REGION] == region and country not in price:
                    price[country] = None
                    save = True

            if save:
                LOG.info('Saving {} ({}) into prices'.format(final[TITLE], nsuid))
                prices_db.save(price)


def find_and_save_all_games():
    wishlisted_count = get_wishlisted_count()

    for system in SYSTEMS.keys():
        find_and_save_games(system, wishlisted_count)
