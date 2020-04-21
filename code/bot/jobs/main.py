import logging

from bot.jobs import games as games_job
from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job
from bot.jobs.util import track
from db.mongo import JobDatabase

LOG = logging.getLogger('jobs')


@track(name='games')
def games():
    return games_job.update_all_games()


@track(name='prices')
def prices():
    return prices_job.update_prices()


@track(name='submissions')
def submissions():
    return submissions_job.update_submissions()


@track(name='wishlists')
def wishlists():
    return wishlist_job.notify_users()


@track(name='update', history=True)
def update():
    results = [
        games(),
        prices(),
        submissions(),
        wishlists()
    ]

    return ' - '.join(results)


def check_last_update():
    last_run = JobDatabase().load('_update')

    if not last_run:
        LOG.info('job.update does not exists')
        return

    if last_run.end:
        LOG.info('job.update finished correctly')
    else:
        LOG.info('job.update did not finish correctly')
        update()
