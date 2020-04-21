import logging
from datetime import datetime

from bot import metacritic
from bot.nintendo import eu
from bot.nintendo import jp
from bot.nintendo import na
from commons.classes import Game
from commons.classes import Price
from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS
from commons.keys import EU
from commons.keys import JP
from commons.keys import NA
from commons.keys import REGION
from commons.keys import SYSTEM
from db.mongo import GamesDatabase
from db.mongo import PricesDatabase
from db.mongo import WishlistDatabase

LOG = logging.getLogger('jobs.games')

new_game_finders = {
    NA: na.list_new_games,
    EU: eu.list_new_games,
    JP: jp.list_new_games,
}


TITLE_FIXES = {
    '#': '',
    'Â®': '®',
    'Ã©': 'é',
    'Ã': 'Û',
    'Û¼': 'ü',
    '&#8482;': '',
    '&333;': 'o',
    '\\\\27': "'",
    '\\\\x26': '&',
    '\\\\u002D': '-',
}


def update_games(system, wishlist_counts):
    now = datetime.utcnow()
    games_db = GamesDatabase()
    prices_db = PricesDatabase()

    games = {game.id: game for game in games_db.load_all(filter={SYSTEM: system})}

    new_games_found = {}

    for region in REGIONS:
        saved_games = [game.nsuids[region] for game in games.values() if game.nsuids.get(region)]

        for nsuid, new_game in new_game_finders[region](system, saved_games):
            new_games_found[region] = new_games_found.get(region, 0) + 1

            game = games.get(new_game.id, Game(_id=new_game.id, system=system))
            game.nsuids[region] = new_game.nsuids.get(region)

            title = new_game.titles.get(region)

            for lookup, replacement in TITLE_FIXES.items():
                if lookup in title:
                    title = title.replace(lookup, replacement)

            game.titles[region] = title

            game.release_dates[region] = new_game.release_dates.get(region)
            game.categories += new_game.categories
            game.categories = list(set(game.categories))

            game.number_of_players = max([game.number_of_players, new_game.number_of_players])
            game.published_by_nintendo = any([game.published_by_nintendo, new_game.published_by_nintendo])

            game.free_to_play = any([game.free_to_play, new_game.free_to_play])

            for country, website in new_game.websites.items():
                if website:
                    game.websites[country] = website

            games[game.id] = game

    prices = {price.id: price for price in prices_db.load_all()}

    for game_id, game in games.items():
        week = str(int(now.strftime("%V")))
        game.wishlisted_history[week] = wishlist_counts.get(game_id, 0)
        game.wishlisted = game.wishlisted_average

        if game.scores.next_update < now:
            game.scores = metacritic.get_scores(system, game.titles.values())

        try:
            GamesDatabase().save(game)
        except Exception as e:
            LOG.error(f'Error saving {game}: {str(e)}')
            continue

        for region, nsuid in game.nsuids.items():
            if not nsuid:
                continue

            save = False

            price = prices.get(nsuid)

            if not price:
                save = True
                price = Price(
                    _id=nsuid,
                    game_id=game.id,
                    system=system,
                    region=region
                )

            for country, details in COUNTRIES.items():
                if details[REGION] == region and country not in price.prices:
                    price.prices[country] = None
                    save = True

            if save:
                LOG.info(f'Saving {game.title} ({nsuid}) into prices')
                prices_db.save(price)

    return f'{system} games found: {new_games_found}'


def get_wishlisted_count():
    wishlist_db = WishlistDatabase()

    counts = {}

    for wishlist in wishlist_db.load_all():
        for game_id in wishlist.games:
            counts[game_id] = counts.get(game_id, 0) + 1

    return counts


def update_all_games():
    LOG.info('Running')

    wishlist_counts = get_wishlisted_count()

    results = []

    for system in SYSTEMS.keys():
        result = update_games(system, wishlist_counts)
        results.append(result)

    LOG.info('Finished')

    return '/'.join(results)
