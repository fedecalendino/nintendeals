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
    LOG.info(' Looking for Nintendo Switch Deals on NA Region')

    na_games, na_added_games = na.get_games(system=SWITCH)

    LOG.info(' Deals found: {}'.format(len(na_games)))
    LOG.info(' New deals since last update: {}'.format(len(na_added_games)))

    LOG.info(' ')
    LOG.info(' Building reddit post')
    na_post = na.make_post(na_games)

    LOG.info(' Posting deals to subreddit: {}'.format(SWITCH_SUBREDDIT))
    Reddit.instance().post(
        SWITCH_SUBREDDIT,
        NA_,
        SWITCH,
        SWITCH_POST_FREQUENCY,
        '[{}] Current eShop deals',
        na_post,
        na_added_games
    )

