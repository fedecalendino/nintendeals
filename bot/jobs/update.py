import logging

from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job


LOG = logging.getLogger('jobs.update')


def update():
    LOG.info('Updating')

    prices_job.find_and_save_prices()
    submissions_job.update_submissions()
    wishlist_job.notify_users()
