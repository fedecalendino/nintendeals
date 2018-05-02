# Standard
import logging
from operator import itemgetter

# Modules
from app.nintendo import common
from app.nintendo import na
from app.nintendo import eu
from app.nintendo import jp

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

    for system, properties in SYSTEMS.items():
        games = {}

        for region, alias in properties[system_].items():
            region_games = fetchers[region](system)

            LOG.info('Deals found on {} region: {}'.format(region, len(region_games)))
            games = merge(games, region_games)

        LOG.info('Total deals found: {}'.format(len(games)))

        games = common.find_prices(games)

        games = sorted(games, key=lambda x: x[title_] if title_ in x else x[title_jp_])

        LOG.info(' ')
        LOG.info(' Building reddit post')

        post, regions = common.make_unified_post(games)

        LOG.info(' Posting all deals to subreddit: {}'.format(properties[subreddit_]))

        Reddit.instance().post(
            properties[subreddit_],
            "-".join(regions),
            system,
            properties[frequency_],
            '[{}] Current {} eShop deals'.format("/".join(regions), properties[name_]),
            post
        )

