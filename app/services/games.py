# Standard
import json

# Dependencies
from flask import Blueprint
from flask import Response

# Modules
from app.db.mongo import GamesDatabase

# Statics
from app.commons.keys import *


GAMES_DB = GamesDatabase.instance()

TAG = 'games'

blueprint = Blueprint('services.games', __name__)
blueprint.prefix = "/api/v1/games"


@blueprint.route('', methods=['GET'])
def track():
    response = []

    games = GAMES_DB.load_all({system_: SWITCH_})
    games = sorted(games, key=lambda x: x[title_].lower() if title_ in x else x[title_jp_].lower())

    for game in games:
        if title_ in game:
            title = game[title_]
        else:
            title = game[title_jp_]

        response.append(
            {
                id_: game[id_],
                title_: title,
                region_: [key for key in game[ids_].keys()]
            }
        )

    return Response(json.dumps(response),  mimetype='application/json')
