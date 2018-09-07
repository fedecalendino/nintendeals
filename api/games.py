# Standard
import json
from datetime import datetime

# Dependencies
from flask import Blueprint
from flask import Response

# Modules
from bot.db.mongo import GamesDatabase

# Statics
from bot.commons.config import *
from bot.commons.keys import *


GAMES_DB = GamesDatabase.instance()

TAG = 'games'

blueprint = Blueprint('services.games', __name__)
blueprint.prefix = "/api/v1/games"


@blueprint.route('', methods=['GET'])
def track():
    response = []

    games = GAMES_DB.load_all({system_: SWITCH_})
    games = sorted(games, key=lambda x: x[title_].lower() if title_ in x else x[title_jp_].lower())

    now = datetime.now()

    for game in games:
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        regions = [key for key in REGIONS.keys() if key in game[ids_].keys()]

        players = game[number_of_players_]

        # Formatting number of players
        if players is None or players == 0:
            players = 'N/A'
        elif players == 1:
            players = '1 player'
        elif players == 2:
            players = '2 players'
        else:
            players = 'up to {} players'.format(players)
        
        item = {
            id_: game[id_],
            title_: title,
            region_: regions,
            release_date_: game[release_date_],
            number_of_players_: players,
            websites_: {}
        }

        if scores_ in game:
            item[scores_] = {
                metascore_: game[scores_][metascore_] if metascore_ in game[scores_] else None,
                userscore_: game[scores_][userscore_] if userscore_ in game[scores_] else None
            }
            
        if websites_ in game:
            item[websites_] = game[websites_]

        response.append(item)

    return Response(json.dumps(response),  mimetype='application/json')
