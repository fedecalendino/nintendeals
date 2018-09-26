# Standard
import time
import traceback
import logging
import threading

# Modules
from bot.db.util import load_all_games

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


def build_submission(games, filtered, countries):
    content = generator.make_post(games, countries)

    if len(filtered) > 0:
        content = content + '\n' + generator.make_post(filtered, countries, filtered=True)

    return content


def build_country_comments(games, countries):
    country_comments = {}

    for country, country_details in countries:
        LOG.info('Building reddit comment for {} {}'.format(country_details[flag_], country))

        for attempt in range(0, 7):
            comment_content = generator.make_comment(
                games,
                country,
                country_details,
                disable_fulltitles=attempt in [1, 3, 4, 5, 6],
                disable_urls=attempt in [2, 3, 4, 5, 6],
                disable_fullprice=attempt in [5, 6],
                disable_decimals=attempt in [6]
            )

            if len(comment_content) < 10000:
                country_comments[country] = comment_content
                break

    return country_comments


def update_posts():

    for system, system_details in SYSTEMS.items():
        LOG.info('🏷️ > Looking up prices for {}'.format(system))
        prices.fetch_prices(system)

        LOG.info('Loading games')
        games = load_all_games(
            filter={system_: system},
            on_sale_only=True,
            add_relevance=True
        )

        selected = []
        filtered = []

        LOG.info('Filter by relevance')
        for game in games:
            if game[relevance_] > 0:
                selected.append(game)
            else:
                filtered.append(game)

        countries = [
            (country, country_details)
            for country, country_details in COUNTRIES.items()
            if country_details[region_] in system_details[system_].keys()
        ]

        LOG.info('Building reddit post')

        title = 'Current {} eShop deals'.format(system_details[name_])
        submission = build_submission(selected, filtered, countries)
        country_comments = build_country_comments(selected, countries)

        LOG.info('Posting {}\'s deals to subreddit/s: {}'.format(system, system_details[subreddit_]))

        for subreddit in system_details[subreddit_]:
            sub_id = Reddit.instance().submit(
                subreddit,
                system,
                title,
                submission
            )

            for country, country_details in countries:
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
