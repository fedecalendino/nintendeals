from collections import namedtuple
from http import HTTPStatus

import flask
from flask import Response

from commons.settings import API_KEY
from commons.settings import PUBLIC_KEY

Error = namedtuple('Error', ['message', 'mimetype', 'code'])

INVALID_API_KEY = Error(
    message='{"error": "invalid api key"}',
    mimetype="application/json",
    code=HTTPStatus.UNAUTHORIZED
)


INVALID_JOB = Error(
    message='{"error": "invalid job"}',
    mimetype="application/json",
    code=HTTPStatus.NOT_FOUND
)


def validate_api_key():
    api_key = flask.request.args.get('api_key')

    if api_key != API_KEY:
        return Response(INVALID_API_KEY.message, mimetype=INVALID_API_KEY.mimetype, status=INVALID_API_KEY.code)

    return None


def validate_public_key():
    api_key = flask.request.args.get('api_key')

    if api_key != PUBLIC_KEY:
        return Response(INVALID_API_KEY.message, mimetype=INVALID_API_KEY.mimetype, status=INVALID_API_KEY.code)

    return None
