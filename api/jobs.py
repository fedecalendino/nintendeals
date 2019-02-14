from threading import Thread

from flask import Blueprint
from flask import Response

from api.util import validate

from bot import jobs

TAG = 'jobs'

blueprint = Blueprint(TAG, __name__)
blueprint.prefix = f"/api/{TAG}"


def run_job(target, message):
    error = validate()

    if error:
        return error

    Thread(target=target, args=[]).start()

    return Response(message, mimetype="application/json")


@blueprint.route('/games', methods=['GET'])
def games():
    return run_job(
        jobs.main.games,
        'Updating: games'
    )


@blueprint.route('/submissions', methods=['GET'])
def submissions():
    return run_job(
        jobs.main.submissions,
        'Updating: submissions'
    )


@blueprint.route('/update', methods=['GET'])
def prices():
    return run_job(
        jobs.main.prices_submissions_notifications,
        'Updating: prices, submissions, notifications'
    )

