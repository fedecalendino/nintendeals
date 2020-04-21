import logging

from bot.reddit import Reddit
from bot.submissions import country_generator
from bot.submissions import main_generator
from commons.config import COUNTRIES
from commons.config import SYSTEMS
from commons.keys import SUBREDDITS
from commons.settings import USER_SUBREDDIT
from db.util import get_games_on_sale

LOG = logging.getLogger('jobs.submissions')


def update_submissions():
    updated_submissions = 0

    reddit = Reddit()

    for system, details in SYSTEMS.items():
        games, sales = get_games_on_sale(system=system)

        submissions = {}

        for country in COUNTRIES:
            title, content, total_new_sales, total_sales = country_generator.generate(games, sales, system, country)

            LOG.info(f'Generated post for {country}: {len(content)} characters')
            
            try:
                sub = reddit.submit(system, USER_SUBREDDIT, title, content, country=country)
                sub.new_sales = total_new_sales
                sub.total_sales = total_sales

                submissions[sub.id] = sub

                updated_submissions += 1
            except Exception as e:
                print(content)
                LOG.error(f'Error with post for {country}: {len(content)} characters')
                raise e

        title, content = main_generator.generate(games, sales, submissions, system)

        LOG.info(f'Generated post for {system}: {len(content)} characters')
        
        for subreddit in details[SUBREDDITS]:
            try:
                reddit.submit(system, subreddit, title, content)
                updated_submissions += 1
            except Exception as e:
                print(content)
                raise e

    return f'Updated submissions: {updated_submissions}'

