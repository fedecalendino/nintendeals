import logging

from bot.jobs import games as games_job
from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job


LOG = logging.getLogger('jobs.main')


def games():
    LOG.info('Updating: games')

    games_job.update_all_games()

    LOG.info('Finished')


def submissions():
    LOG.info('Updating: submissions')

    submissions_job.update_submissions()

    LOG.info('Finished')


def prices_submissions_notifications():
    LOG.info('Updating: prices, submissions, notifications')

    prices_job.update_prices()
    submissions_job.update_submissions()
    wishlist_job.notify_users()

    LOG.info('Finished')
