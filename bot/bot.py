# Standard
import time
import traceback
import logging
import threading

# Modules
from bot.db.util import load_games

from bot.nintendo import eu
from bot.nintendo import jp
from bot.nintendo import na
from bot.nintendo import prices

from bot.metacritic import scores

from bot.posts import generator

from bot.reddit.reddit import Reddit

from bot.wishlist.wishlist import notify

# Statics
from bot.commons.config import *
from bot.commons.keys import *
from bot.commons.util import *


LOG = logging.getLogger('🤖')


fetchers = {
    NA_: na.find_games,
    EU_: eu.find_games,
    JP_: jp.find_games
}


def update_posts():
    LOG.info('🏷️  > Looking up prices')
    # prices.fetch_prices()

    for system, system_details in SYSTEMS.items():
        LOG.info('Loading games')
        games = load_games(
            filter={system_: system},
            on_sale_only=True,
            add_relevance=True
        )

        countries = [
            country for country, country_details in COUNTRIES.items()
                if country_details[region_] in system_details[system_].keys()
        ]

        LOG.info('Building reddit post')

        title = 'Current {} eShop deals'.format(system_details[name_])
        submission = generator.make_post(games, countries)
        country_comments = generator.build_country_comments(games, countries)

        LOG.info('Posting {}\'s deals to subreddit/s: {}'.format(system, system_details[subreddit_]))

        for subreddit in system_details[subreddit_]:
            sub_id = Reddit.instance().submit(
                subreddit,
                system,
                title,
                submission
            )

            for country in countries:
                comment_content = country_comments[country]

                try:
                    Reddit.instance().comment(
                        sub_id,
                        country,
                        comment_content
                    )
                except Exception as e:
                    LOG.error(e)
                    LOG.error(comment_content)

                time.sleep(11)

            LOG.info('Updating post with comment links')

            Reddit.instance().submit(
                subreddit,
                system,
                'Current {} eShop deals'.format(system_details[name_]),
                submission
            )

    try:
        if REDDIT_USERNAME == 'nintendeals':
            LOG.info('⭐ Sending wishlist notifications')
            notify()
    except Exception as e:
        LOG.error(e)
        traceback.print_exc()


def inbox():
    while True:
        try:
            LOG.info('📥 > Checking reddit inbox')
            Reddit.instance().inbox()
        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        time.sleep(15)


def game_lookup():
    while True:
        try:
            for system, system_details in SYSTEMS.items():
                for region, alias in system_details[system_].items():
                    LOG.info('')
                    LOG.info('🎮 > Looking up games for {} on {}'.format(system, region))
                    try:
                        fetchers[region](system)
                    except Exception as e:
                        LOG.error('🎮 > Error fetching game for {} on {}'.format(system, region))
                        LOG.error(e)
                        traceback.print_exc()

        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        time.sleep(2 * 60 * 60)


def score_lookup():
    while True:
        try:
            LOG.info('💯 > Fetching scores for each game')
            scores.fetch_scores()
        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        time.sleep(12 * 20 * 60)


def main():
    LOG.info('  Mongo: {}'.format(MONGODB_URI))
    LOG.info('  Reddit Username: {}'.format(REDDIT_USERNAME))

    LOG.info('Setting up inbox thread')
    threading.Thread(target=inbox).start()

    LOG.info('Setting up game lookup thread')
    threading.Thread(target=game_lookup).start()

    LOG.info('Setting up score lookup thread')
    threading.Thread(target=score_lookup).start()

    while True:
        try:
            LOG.info('🌐 Updating posts')
            update_posts()
        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        time.sleep(30 * 60)
