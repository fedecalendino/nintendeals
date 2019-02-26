import logging
from datetime import datetime

from bot import metacritic
from db.mongo import GamesDatabase
from db.mongo import PricesDatabase
from db.mongo import WishlistDatabase

from bot.nintendo import eu
from bot.nintendo import jp
from bot.nintendo import na

from commons.classes import Game
from commons.classes import Price

from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS

from commons.keys import DB
from commons.keys import EU
from commons.keys import JP
from commons.keys import NA
from commons.keys import REGION
from commons.keys import SYSTEM


LOG = logging.getLogger('jobs.games')


def get_wishlisted_count():
    wishlist_db = WishlistDatabase()

    counts = {}

    for wishlist in wishlist_db.load_all():
        for game_id in wishlist.games:
            counts[game_id] = counts.get(game_id, 0) + 1

    return counts


def merge_game(game_id, game, system):
    final = Game(_id=game_id, system=system)

    if game.get(DB):
        final.scores =  game.get(DB).scores

    for region in REGIONS:
        regional = game.get(region, None)

        if not regional:
            continue

        final.nsuids[region] = regional.nsuids.get(region)
        final.titles[region] = regional.titles.get(region)\
            .replace('Â®', '®')\
            .replace('Ã©', 'é')\
            .replace('Ã', 'Û')\
            .replace('Û¼', 'ü')\
            .replace('&#8482;', '')

        final.release_dates[region] = regional.release_dates.get(region)
        final.categories += regional.categories

        final.number_of_players = max([final.number_of_players, regional.number_of_players])
        final.published_by_nintendo = any([final.published_by_nintendo, regional.published_by_nintendo])

        final.free_to_play = any([final.free_to_play, regional.free_to_play])

        for country, website in regional.websites.items():
            if website:
                final.websites[country] = website

    final.categories = list(set(final.categories))

    return final


def add(games, region, game):
    if not games.get(game.id):
        games[game.id] = {}

    games[game.id][region] = game


def update_games(system, wishlist_counts={}):
    now = datetime.utcnow()
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

    prices = {price.id: price for price in prices_db.load_all()}

    for game_id, game in games.items():
        final = merge_game(game_id, game, system)
        final.wishlisted = wishlist_counts.get(game_id, 0)

        if final.scores.next_update < now:
            final.scores = metacritic.get_scores(system, final.title_en)

        try:
            GamesDatabase().save(final)
        except Exception as e:
            LOG.error(f'Error saving {final.id}: {str(e)}')
            continue

        for region, nsuid in final.nsuids.items():
            if not nsuid:
                continue

            save = False

            price = prices.get(nsuid)

            if not price:
                save = True
                price = Price(
                    _id=nsuid,
                    game_id=final.id,
                    system=system,
                    region=region
                )

            for country, details in COUNTRIES.items():
                if details[REGION] == region and country not in price.prices:
                    price.prices[country] = None
                    save = True

            if save:
                LOG.info('Saving {} ({}) into prices'.format(final.title, nsuid))
                prices_db.save(price)


def update_all_games():
    LOG.info('Running')

    wishlist_counts = get_wishlisted_count()

    for system in SYSTEMS.keys():
        update_games(system, wishlist_counts)

    LOG.info('Finished')
