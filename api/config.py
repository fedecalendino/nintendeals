# Standard
import json

# Dependencies
from flask import Blueprint
from flask import Response

# Statics
from bot.commons.config import *
from bot.commons.keys import *

TAG = 'config'

blueprint = Blueprint('services.config', __name__)
blueprint.prefix = "/api/v1/config"


@blueprint.route('', methods=['GET'])
def track():
    countries = {}

    for key, details in COUNTRIES.items():
        countries[key] = {key_: key, name_: details[name_], flag_: details[flag_], region_: details[region_]}

    response = {
        username_: REDDIT_USERNAME,
        countries_: countries
    }

    return Response(json.dumps(response),  mimetype='application/json')
