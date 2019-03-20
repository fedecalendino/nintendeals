import logging

from bot.reddit import Reddit
from bot.submissions import generator

from db.util import get_games_on_sale

from commons.config import COUNTRIES
from commons.config import SYSTEMS

from commons.keys import SUBREDDITS

from commons.settings import USER_SUBREDDIT


LOG = logging.getLogger('jobs.submissions')


def update_submissions():
    updated_submissions = 0

    reddit = Reddit()

    for system, details in SYSTEMS.items():
        games, sales = get_games_on_sale(system=system)

        submissions = {}

        for country in COUNTRIES:
            title, content = generator.generate_country_post(games, sales, system, country)

            sub = reddit.submit(system, USER_SUBREDDIT, title, content, country=country)
            submissions[sub.id] = sub

            updated_submissions += 1

        title, content = generator.generate_main_post(games, sales, submissions, system)

        for subreddit in details[SUBREDDITS]:
            reddit.submit(system, subreddit, title, content)

            updated_submissions += 1

    return f'Updated submissions: {updated_submissions}'

