"""Provide exception classes for the prawcore package."""

import sys


if sys.version_info[0] == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


class PrawcoreException(Exception):
    """Base exception class for exceptions that occur within this package."""


class InvalidInvocation(PrawcoreException):
    """Indicate that the code to execute cannot be completed."""


class RequestException(PrawcoreException):
    """Indicate that there was an error with the incomplete HTTP request."""

    def __init__(self, original_exception, request_args, request_kwargs):
        """Initialize a RequestException instance.

        :param original_exception: The original exception that occurred.
        :param request_args: The arguments to the request function.
        :param request_kwargs: The keyword arguments to the request function.

        """
        self.original_exception = original_exception
        self.request_args = request_args
        self.request_kwargs = request_kwargs
        super(RequestException, self).__init__('error with request {}'
                                               .format(original_exception))


class ResponseException(PrawcoreException):
    """Indicate that there was an error with the completed HTTP request."""

    def __init__(self, response):
        """Initialize a ResponseException instance.

        :param response: A requests.response instance.

        """
        self.response = response
        super(ResponseException, self).__init__('received {} HTTP response'
                                                .format(response.status_code))


class OAuthException(PrawcoreException):
    """Indicate that there was an OAuth2 related error with the request."""

    def __init__(self, response, error, description):
        """Intialize a OAuthException instance.

        :param response: A requests.response instance.
        :param error: The error type returned by reddit.
        :param description: A description of the error when provided.

        """
        self.error = error
        self.description = description
        self.response = response
        message = '{} error processing request'.format(error)
        if description:
            message += ' ({})'.format(description)
        PrawcoreException.__init__(self, message)


class BadJSON(ResponseException):
    """Indicate the response did not contain valid JSON."""


class BadRequest(ResponseException):
    """Indicate invalid parameters for the request."""


class Conflict(ResponseException):
    """Indicate a conflicting change in the target resource."""


class Forbidden(ResponseException):
    """Indicate the authentication is not permitted for the request."""


class InsufficientScope(ResponseException):
    """Indicate that the request requires a different scope."""


class InvalidToken(ResponseException):
    """Indicate that the request used an invalid access token."""


class NotFound(ResponseException):
    """Indicate that the requested URL was not found."""


class Redirect(ResponseException):
    """Indicate the request resulted in a redirect.

    This class adds the attribute ``path``, which is the path to which the
    response redirects.

    """

    def __init__(self, response):
        """Initialize a Redirect exception instance..

        :param response: A requests.response instance containing a location
        header.

        """
        path = urlparse(response.headers['location']).path
        self.path = path[:-5] if path.endswith('.json') else path
        self.response = response
        PrawcoreException.__init__(self, 'Redirect to {}'.format(self.path))


class ServerError(ResponseException):
    """Indicate issues on the server end preventing request fulfillment."""


class TooLarge(ResponseException):
    """Indicate that the request data exceeds the allowed limit."""


class UnavailableForLegalReasons(ResponseException):
    """Indicate that the requested URL is unavilable due to legal reasons."""
