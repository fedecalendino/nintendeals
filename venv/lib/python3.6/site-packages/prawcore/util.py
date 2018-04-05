"""Provide utility for the prawcore package."""
from .exceptions import Forbidden, InsufficientScope, InvalidToken


_auth_error_mapping = {403: Forbidden,
                       'insufficient_scope': InsufficientScope,
                       'invalid_token': InvalidToken}


def authorization_error_class(response):
    """Return an exception instance that maps to the OAuth Error.

    :param response: The HTTP response containing a www-authenticate error.

    """
    message = response.headers.get('www-authenticate')
    if message:
        error = message.replace('"', '').rsplit('=', 1)[1]
    else:
        error = response.status_code
    return _auth_error_mapping[error](response)
