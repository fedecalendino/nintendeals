from collections import namedtuple
from http import HTTPStatus

import flask
from flask import Response

from commons.settings import API_KEY

Error = namedtuple('Error', ['message', 'mimetype', 'code'])

INVALID_API_KEY = Error(
    message='{"error": "invalid api key"}',
    mimetype="application/json",
    code=HTTPStatus.UNAUTHORIZED
)


def validate():
    api_key = flask.request.args.get('api_key')

    if api_key != API_KEY:
        return Response(INVALID_API_KEY.message, mimetype=INVALID_API_KEY.mimetype, status=INVALID_API_KEY.code)

    return None
