# Standard
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Modules
from app.db.mongo import GamesDatabase
from app.metacritic import metacritic

# Constants
from app.commons.keys import *


LOG = logging.getLogger('metacritic.scores')


GAMES_DB = GamesDatabase.instance()


def fetch_scores():

    for game in GAMES_DB.load_all():
        if scores_ not in game:
            game[scores_] = {}

        if last_update_ not in game[scores_]:
            game[scores_][last_update_] = datetime.now() + relativedelta(days=-30)

        if game[scores_][last_update_] + relativedelta(days=+14) > datetime.now():
            continue

        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        metascore, userscore = metacritic.get_score(game[system_], title)

        game[scores_][last_update_] = datetime.now()

        if metascore is not None or userscore is not None:
            game[scores_][metascore_] = metascore
            game[scores_][userscore_] = userscore

            LOG.info('Scores for {} found: {}/{}'.format(title, metascore, userscore))
        else:
            LOG.info('Scores for {} not found'.format(title))

        game[scores_][last_update_] = datetime.now()

        GAMES_DB.save(game)
