# Standard
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Modules
from bot.db.mongo import GamesDatabase
from bot.metacritic import metacritic

# Commons
from bot.commons.keys import *
from bot.commons.util import get_title


LOG = logging.getLogger('💯')


GAMES_DB = GamesDatabase.instance()


def fetch_scores():

    now = datetime.now()

    for game in GAMES_DB.load_all():
        if scores_ not in game:
            game[scores_] = {}

        if last_update_ not in game[scores_]:
            game[scores_][last_update_] = now + relativedelta(days=-30)

        if metascore_ not in game[scores_] or game[scores_][metascore_] == '-' or \
                userscore_ not in game[scores_] or game[scores_][userscore_] == '-':
            
            if game[scores_][last_update_] + relativedelta(days=+7) > now:
                continue
        else:
            if game[scores_][last_update_] + relativedelta(days=+14) > now:
                continue

        title = game[title_metacritic_] if title_metacritic_ in game else get_title(game)
            
        metascore, userscore, system = metacritic.get_score(game[system_], title)

        if metascore is not None or userscore is not None:
            game[scores_][metascore_] = metascore
            game[scores_][userscore_] = userscore
            game[scores_][system_] = system

            LOG.info('Scores for {} found on {}: {}/{}'.format(title, system, metascore, userscore))
        else:
            LOG.info('Scores for {} not found'.format(title))

        game[scores_][last_update_] = now

        GAMES_DB.save(game)
