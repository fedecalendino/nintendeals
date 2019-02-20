from threading import Thread

from flask import request
from flask import Blueprint
from flask import Response

from api.util import validate

from bot import jobs

TAG = 'jobs'

blueprint = Blueprint(TAG, __name__)
blueprint.prefix = f"/api/{TAG}"


def run_job(target, message, source=None):
    error = validate()

    if error:
        return error

    Thread(target=target, args=[source]).start()

    return Response(message, mimetype="application/json")


@blueprint.route('/games', methods=['GET'])
def games():
    return run_job(
        jobs.main.games,
        'Updating: games',
        source=request.args.get('source')
    )


@blueprint.route('/submissions', methods=['GET'])
def submissions():
    return run_job(
        jobs.main.submissions,
        'Updating: submissions',
        source=request.args.get('source')
    )


@blueprint.route('/update', methods=['GET'])
def prices():
    return run_job(
        jobs.main.prices_submissions_notifications,
        'Updating: prices, submissions, notifications',
        source=request.args.get('source')
    )

