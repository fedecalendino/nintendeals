from threading import Thread

from flask import Blueprint
from flask import Response

from api.util import INVALID_JOB
from api.util import validate_api_key
from bot.jobs import main as jobs

TAG = 'jobs'

blueprint = Blueprint(TAG, __name__)
blueprint.prefix = f"/api/{TAG}"

JOBS = {
    'games': jobs.games,
    'prices': jobs.prices,
    'submissions': jobs.submissions,
    'wishlists': jobs.wishlists,
    'update': jobs.update
}


@blueprint.route('/<string:name>', methods=['GET'])
def run(name):
    message = validate_api_key()

    if message:
        return message

    job = JOBS.get(name)

    if not job:
        return Response(INVALID_JOB.message, mimetype=INVALID_JOB.mimetype, status=INVALID_JOB.code)

    Thread(target=job).start()

    return Response(f'Running: {name}')

