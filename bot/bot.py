# Standard
import time
import traceback
import logging

# Modules
from bot.db.mongo import GamesDatabase

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

LOG = logging.getLogger('bot')

GAMES_DB = GamesDatabase.instance()

fetchers = {
    NA_: na.find_games,
    EU_: eu.find_games,
    JP_: jp.find_games
}


def check_inbox():
    LOG.info(' ')
    LOG.info(' Checking reddit inbox')
    Reddit.instance().inbox()


def run():
    LOG.info(' ')

    for system, system_details in SYSTEMS.items():

        for region, alias in system_details[system_].items():
            LOG.info(' ')
            LOG.info('Fetching games for {}'.format(region))

            try:
                fetchers[region](system)
            except Exception as e:
                print(e)
                print('error fetching {} games'.format(region))

            check_inbox()

        check_inbox()

        LOG.info(' ')
        LOG.info('Fetching scores for each game')
        scores.fetch_scores()

        check_inbox()

        LOG.info(' ')
        LOG.info('Fetching prices for each game')
        prices.fetch_prices(system)

        LOG.info(' ')
        LOG.info('Sorting games by title')
        games = GAMES_DB.load_all({system_: system})
        games = sorted(games, key=lambda x: x[title_].lower() if title_ in x else x[title_jp_].lower())

        countries = [
            (country, country_details)
            for country, country_details in COUNTRIES.items()
            if country_details[region_] in system_details[system_].keys()
        ]

        LOG.info(' ')
        LOG.info('Building reddit post')
        sub_content = generator.make_post(games, countries)

        LOG.info('Posting {}\'s deals to subreddit/s: {}'.format(system, system_details[subreddit_]))

        for subreddit in system_details[subreddit_]:
            sub_id = Reddit.instance().submit(
                subreddit,
                system,
                'Current {} eShop deals'.format(system_details[name_]),
                sub_content
            )

            for country, country_details in countries:
                LOG.info('Building reddit comment for {} {} on {}'.format(country_details[flag_], country, sub_id))
                comment_content = generator.make_comment(games, country, country_details)

                if len(comment_content) > 10000:
                    comment_content = generator.make_comment(games, country, country_details, disable_urls=True)

                    if len(comment_content) > 10000:
                        comment_content = generator.make_comment(games, country, country_details, disable_urls=True, disable_fullprice=True)

                        if len(comment_content) > 10000:
                            comment_content = generator.make_comment(games, country, country_details, disable_urls=True,
                                                                     disable_fullprice=True, disable_decimals=True)

                try:
                    Reddit.instance().comment(
                        sub_id,
                        country,
                        comment_content
                    )
                except Exception as e:
                    print(e)
                    print(comment_content)

                time.sleep(15)

                check_inbox()

            LOG.info('Updating post with comment links')

            Reddit.instance().submit(
                subreddit,
                system,
                'Current {} eShop deals'.format(system_details[name_]),
                sub_content
            )

    check_inbox()

    LOG.info(' ')
    LOG.info('Sending wishlist notifications')
    notify()


def main():
    LOG.info(' Start up')
    LOG.info(' ')

    LOG.info("  Mongo: {}".format(MONGODB_URI))
    LOG.info("  Reddit Username: {}".format(REDDIT_USERNAME))
    LOG.info(' ')

    reset = 60

    count = reset

    while True:
        try:
            check_inbox()

            if count >= reset:
                LOG.info(' Running Bot ({})'.format(count))
                run()
        except Exception as e:
            LOG.error(e)
            traceback.print_exc()

        if count >= reset:
            count = 0
        else:
            count += 1

        LOG.info(' Sleeping for {} seconds'.format(UPDATE_FREQUENCY))
        time.sleep(UPDATE_FREQUENCY)
