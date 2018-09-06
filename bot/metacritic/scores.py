# Standard
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Modules
from bot.db.mongo import GamesDatabase
from bot.metacritic import metacritic

# Constants
from bot.commons.keys import *


LOG = logging.getLogger('💯')


GAMES_DB = GamesDatabase.instance()


def fetch_scores():

    for game in GAMES_DB.load_all():
        if scores_ not in game:
            game[scores_] = {}

        if last_update_ not in game[scores_]:
            game[scores_][last_update_] = datetime.now() + relativedelta(days=-30)

        if system_ not in game[scores_] or game[scores_][system_] is None:
            if game[scores_][last_update_] + relativedelta(days=+7) > datetime.now():
                continue
        else:
            if game[scores_][last_update_] + relativedelta(days=+14) > datetime.now():
                continue

        if title_metacritic_ in game:
            title = game[title_metacritic_]
        elif title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]
            
        metascore, userscore, system = metacritic.get_score(game[system_], title)

        if metascore is not None or userscore is not None:
            game[scores_][metascore_] = metascore
            game[scores_][userscore_] = userscore
            game[scores_][system_] = system

            LOG.info('Scores for {} found on {}: {}/{}'.format(title, system, metascore, userscore))
        else:
            LOG.info('Scores for {} not found'.format(title))

        game[scores_][last_update_] = datetime.now()

        GAMES_DB.save(game)
