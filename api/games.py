# Standard
import json

# Dependencies
from flask import Blueprint
from flask import Response

# Modules
from bot.db.util import load_all_games

# Statics
from bot.commons.config import *
from bot.commons.keys import *


TAG = 'games'


blueprint = Blueprint('services.games', __name__)
blueprint.prefix = "/api/v1/games"


@blueprint.route('', methods=['GET'])
def track():
    response = []

    for game in load_all_games(filter={system_: SWITCH_}, exclude_prices=True):
        regions = [key for key in REGIONS.keys() if key in game[ids_].keys()]

        players = game[number_of_players_]

        # Formatting number of players
        if players is None or players == 0:
            players = 'n/a'
        elif players == 1:
            players = '1 player'
        elif players == 2:
            players = '2 players'
        else:
            players = 'up to {} players'.format(players)
        
        item = {
            id_: game[id_],
            title_: game[final_title_],
            region_: regions,
            release_date_: game[release_date_],
            number_of_players_: players,
            websites_: {}
        }

        if websites_ in game:
            item[websites_] = game[websites_]

        if scores_ in game:
            item[scores_] = {
                metascore_: game[scores_][metascore_] if metascore_ in game[scores_] else None,
                userscore_: game[scores_][userscore_] if userscore_ in game[scores_] else None
            }

        if features_ in game:
            item[features_] = game[features_]

        response.append(item)

    response = sorted(response, key=lambda g: g[release_date_], reverse=True)

    return Response(json.dumps(response),  mimetype='application/json')
