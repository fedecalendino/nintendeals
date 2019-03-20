from db.mongo import JobDatabase

from bot.jobs import games as games_job
from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job

from commons.classes import Job


def run(name, target, source=None):
    job = Job(_id=name)
    job.source = source
    JobDatabase().save(job)

    target()

    job.finish()
    JobDatabase().save(job)


def games(source=None):
    run('games', games_job.update_all_games, source)


def submissions(source=None):
    run('submissions', submissions_job.update_submissions, source)


def wishlists(source=None):
    run('wishlists', wishlist_job.notify_users, source)


def games_prices_submissions_notifications(source=None):
    run('games', games_job.update_all_games, source)
    run('prices', prices_job.update_prices, source)
    run('submissions', submissions_job.update_submissions, source)
    run('wishlists', wishlist_job.notify_users, source)

