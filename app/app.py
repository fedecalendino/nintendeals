# Standard
import logging

# Modules
from app.nintendo import na
from app.reddit.reddit import Reddit

# Statics
from app.commons.config import *
from app.commons.keys import *


LOG = logging.getLogger('bot')


def run():
    LOG.info(' ')

    for system, properties in SYSTEMS.items():
        LOG.info(' Looking for {} deals on NA Region'.format(system))

        na_games, na_added_games = na.get_games(system=system)

        LOG.info(' Deals found: {}'.format(len(na_games)))
        LOG.info(' New deals since last update: {}'.format(len(na_added_games)))

        LOG.info(' ')
        LOG.info(' Building reddit post')
        na_post = na.make_post(na_games)

        LOG.info(' Posting deals to subreddit: {}'.format(properties[subreddit_]))
        Reddit.instance().post(
            properties[subreddit_],
            NA_,
            system,
            properties[frequency_],
            '[{}] Current {} eShop deals'.format('{}', properties[name_]),
            na_post,
            na_added_games
        )
