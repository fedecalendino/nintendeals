# Standard
import time
import logging

# Modules
from app.nintendo import common
from app.nintendo import na
from app.nintendo import eu
from app.nintendo import jp

from app.posts import generator

from app.commons.util import merge

from app.reddit.reddit import Reddit

# Statics
from app.commons.config import *

LOG = logging.getLogger('bot')


fetchers = {
    NA_: na.get_deals,
    EU_: eu.get_deals,
    JP_: jp.get_deals
}


def run():
    LOG.info(' ')

    for system, system_details in SYSTEMS.items():
        games = {}

        for region, alias in system_details[system_].items():
            LOG.info('Fetching deals for region: {}'.format(region))

            region_games = fetchers[region](system)

            LOG.info('Deals found on {} region: {}'.format(region, len(region_games)))
            games = merge(games, region_games)

        countries = [
            (country, country_details)
            for country, country_details in COUNTRIES.items()
            if country_details[region_] in system_details[system_].keys()
        ]

        LOG.info('Total deals found: {}'.format(len(games)))

        games = common.find_prices_and_scores(games)

        LOG.info('Sorting deals by game title')
        games = sorted(games, key=lambda x: x[title_] if title_ in x else x[title_jp_])

        LOG.info(' ')
        LOG.info('Building reddit post')
        post = generator.make_post(games, countries)

        LOG.info('Posting all deals to subreddit: {}'.format(system_details[subreddit_]))

        for subreddit in system_details[subreddit_]:
            post_id = Reddit.instance().post(
                subreddit,
                system,
                system_details[frequency_],
                'Current {} eShop deals'.format(system_details[name_]),
                post
            )

            for country, country_details in countries:
                LOG.info('Building reddit comment for {} {} on {}'.format(country_details[flag_], country, post_id))

                comment = generator.make_comment(games, country, country_details)

                Reddit.instance().comment(
                    post_id,
                    country,
                    comment
                )

                time.sleep(15)

            LOG.info('Updating post with comment links')

            Reddit.instance().post(
                subreddit,
                system,
                system_details[frequency_],
                'Current {} eShop deals'.format(system_details[name_]),
                post
            )
