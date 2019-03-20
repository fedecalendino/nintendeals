from bot.jobs import games as games_job
from bot.jobs import prices as prices_job
from bot.jobs import submissions as submissions_job
from bot.jobs import wishlist as wishlist_job


from bot.jobs.util import track


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


@track(name='update')
def update():
    results = [
        games(),
        prices(),
        submissions(),
        wishlists()
    ]

    return ' - '.join(results)
