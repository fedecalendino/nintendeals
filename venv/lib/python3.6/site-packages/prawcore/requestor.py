"""Provides the HTTP request handling interface."""
import requests
from .const import __version__, TIMEOUT
from .exceptions import InvalidInvocation, RequestException


class Requestor(object):
    """Requestor provides an interface to HTTP requests."""

    def __getattr__(self, attribute):
        """Pass all undefined attributes to the _http attribute."""
        if attribute.startswith('__'):
            raise AttributeError
        return getattr(self._http, attribute)

    def __init__(self, user_agent, oauth_url='https://oauth.reddit.com',
                 reddit_url='https://www.reddit.com', session=None):
        """Create an instance of the Requestor class.

        :param user_agent: The user-agent for your application. Please follow
            reddit's user-agent guidlines:
            https://github.com/reddit/reddit/wiki/API#rules
        :param oauth_url: (Optional) The URL used to make OAuth requests to the
            reddit site. (Default: https://oauth.reddit.com)
        :param reddit_url: (Optional) The URL used when obtaining access
            tokens. (Default: https://www.reddit.com)
        :param session: (Optional) A session to handle requests, compatible
            with requests.Session(). (Default: None)
        """
        if user_agent is None or len(user_agent) < 7:
            raise InvalidInvocation('user_agent is not descriptive')

        self._http = session or requests.Session()
        self._http.headers['User-Agent'] = '{} prawcore/{}'.format(
            user_agent, __version__)

        self.oauth_url = oauth_url
        self.reddit_url = reddit_url

    def close(self):
        """Call close on the underlying session."""
        return self._http.close()

    def request(self, *args, **kwargs):
        """Issue the HTTP request capturing any errors that may occur."""
        try:
            return self._http.request(*args, timeout=TIMEOUT, **kwargs)
        except Exception as exc:
            raise RequestException(exc, args, kwargs)
