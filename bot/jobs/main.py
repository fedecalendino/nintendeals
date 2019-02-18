from db.mongo import JobDatabase

from bot.jobs import games as games_job
from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job

from commons.classes import Job


def run(name, target):
    job = Job(_id=name)
    JobDatabase().save(job)

    target()

    job.finish()
    JobDatabase().save(job)


def games():
    run('games', games_job.update_all_games)


def submissions():
    run('submissions', submissions_job.update_submissions)


def prices_submissions_notifications():
    run('update.prices', prices_job.update_prices)
    run('update.submissions', submissions_job.update_submissions)
    run('update.wishlists', wishlist_job.notify_users)

