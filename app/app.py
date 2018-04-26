# Standard
import logging
from operator import itemgetter

# Modules
from app.nintendo import common
from app.nintendo import na
from app.nintendo import eu

from app.commons.util import merge

from app.reddit.reddit import Reddit

# Statics
from app.commons.config import *

LOG = logging.getLogger('bot')


def run():
    LOG.info(' ')

    for system, properties in SYSTEMS.items():
        na_games = na.get_deals(system=system)
        LOG.info('Deals found on NA region: {}'.format(len(na_games)))

        eu_games = eu.get_deals(system=system)
        LOG.info('Deals found on EU region: {}'.format(len(eu_games)))

        games = merge(na_games, eu_games)
        LOG.info('Total deals found: {}'.format(len(games)))

        games = common.find_prices(games)

        games = sorted(games, key=itemgetter(title_))

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

