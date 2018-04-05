"""Provides Authentication and Authorization classes."""
import time
from . import const
from .exceptions import InvalidInvocation, OAuthException, ResponseException
from requests import Request
from requests.status_codes import codes


class BaseAuthenticator(object):
    """Provide the base authenticator object that stores OAuth2 credentials."""

    def __init__(self, requestor, client_id, redirect_uri=None):
        """Represent a single authentication to Reddit's API.

        :param requestor: An instance of :class:`Requestor`.
        :param client_id: The OAuth2 client ID to use with the session.
        :param redirect_uri: (optional) The redirect URI exactly as specified
            in your OAuth application settings on Reddit. This parameter is
            required if you want to use the ``authorize_url`` method, or the
            ``authorize`` method of the ``Authorizer`` class.

        """
        self._requestor = requestor
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def _post(self, url, success_status=codes['ok'], **data):
        response = self._requestor.request('post', url, auth=self._auth(),
                                           data=sorted(data.items()))
        if response.status_code != success_status:
            raise ResponseException(response)
        return response

    def authorize_url(self, duration, scopes, state, implicit=False):
        """Return the URL used out-of-band to grant access to your application.

        :param duration: Either ``permanent`` or ``temporary``. ``temporary``
            authorizations generate access tokens that last only 1
            hour. ``permanent`` authorizations additionally generate a refresh
            token that can be indefinitely used to generate new hour-long
            access tokens. Only ``temporary`` can be specified if ``implicit``
            is set to ``True``.
        :param scopes: A list of OAuth scopes to request authorization for.
        :param state: A string that will be reflected in the callback to
            ``redirect_uri``. This value should be temporarily unique to the
            client for whom the URL was generated for.
        :param implicit: (optional) Use the implicit grant flow (default:
            False). This flow is only available for UntrustedAuthenticators.

        """
        if self.redirect_uri is None:
            raise InvalidInvocation('redirect URI not provided')
        if implicit and not isinstance(self, UntrustedAuthenticator):
            raise InvalidInvocation('Only UntrustedAuthentictor instances can '
                                    'use the implicit grant flow.')
        if implicit and duration != 'temporary':
            raise InvalidInvocation('The implicit grant flow only supports '
                                    'temporary access tokens.')

        params = {'client_id': self.client_id, 'duration': duration,
                  'redirect_uri': self.redirect_uri,
                  'response_type': 'token' if implicit else 'code',
                  'scope': ' '.join(scopes), 'state': state}
        url = self._requestor.reddit_url + const.AUTHORIZATION_PATH
        request = Request('GET', url, params=params)
        return request.prepare().url

    def revoke_token(self, token, token_type=None):
        """Ask Reddit to revoke the provided token.

        :param token: The access or refresh token to revoke.
        :param token_type: (Optional) When provided, hint to Reddit what the
            token type is for a possible efficiency gain. The value can be
            either ``access_token`` or ``refresh_token``.

        """
        data = {'token': token}
        if token_type is not None:
            data['token_type_hint'] = token_type
        url = self._requestor.reddit_url + const.REVOKE_TOKEN_PATH
        self._post(url, success_status=codes['no_content'], **data)


class TrustedAuthenticator(BaseAuthenticator):
    """Store OAuth2 authentication credentials for web, or script type apps."""

    RESPONSE_TYPE = 'code'

    def __init__(self, requestor, client_id, client_secret, redirect_uri=None):
        """Represent a single authentication to Reddit's API.

        :param requestor: An instance of :class:`Requestor`.
        :param client_id: The OAuth2 client ID to use with the session.
        :param client_secret: The OAuth2 client secret to use with the session.
        :param redirect_uri: (optional) The redirect URI exactly as specified
            in your OAuth application settings on Reddit. This parameter is
            required if you want to use the ``authorize_url`` method, or the
            ``authorize`` method of the ``Authorizer`` class.

        """
        super(TrustedAuthenticator, self).__init__(requestor, client_id,
                                                   redirect_uri)
        self.client_secret = client_secret

    def _auth(self):
        return (self.client_id, self.client_secret)


class UntrustedAuthenticator(BaseAuthenticator):
    """Store OAuth2 authentication credentials for installed applications."""

    def _auth(self):
        return (self.client_id, '')


class BaseAuthorizer(object):
    """Superclass for OAuth2 authorization tokens and scopes."""

    def __init__(self, authenticator):
        """Represent a single authorization to Reddit's API.

        :param authenticator: An instance of :class:`BaseAuthenticator`.

        """
        self._authenticator = authenticator
        self._clear_access_token()
        self._validate_authenticator()

    def _clear_access_token(self):
        self._expiration_timestamp = None
        self.access_token = None
        self.scopes = None

    def _request_token(self, **data):
        url = (self._authenticator._requestor.reddit_url +
               const.ACCESS_TOKEN_PATH)
        pre_request_time = time.time()
        response = self._authenticator._post(url, **data)
        payload = response.json()
        if 'error' in payload:  # Why are these OKAY responses?
            raise OAuthException(response, payload['error'],
                                 payload.get('error_description'))

        self._expiration_timestamp = (pre_request_time - 10
                                      + payload['expires_in'])
        self.access_token = payload['access_token']
        if 'refresh_token' in payload:
            self.refresh_token = payload['refresh_token']
        self.scopes = set(payload['scope'].split(' '))

    def _validate_authenticator(self):
        if not isinstance(self._authenticator, self.AUTHENTICATOR_CLASS):
            raise InvalidInvocation('Must use a authenticator of type {}.'
                                    .format(self.AUTHENTICATOR_CLASS.__name__))

    def is_valid(self):
        """Return whether or not the Authorizer is ready to authorize requests.

        A ``True`` return value does not guarantee that the access_token is
        actually valid on the server side.

        """
        return self.access_token is not None \
            and time.time() < self._expiration_timestamp

    def revoke(self):
        """Revoke the current Authorization."""
        if self.access_token is None:
            raise InvalidInvocation('no token available to revoke')

        self._authenticator.revoke_token(self.access_token, 'access_token')
        self._clear_access_token()


class Authorizer(BaseAuthorizer):
    """Manages OAuth2 authorization tokens and scopes."""

    AUTHENTICATOR_CLASS = BaseAuthenticator

    def __init__(self, authenticator, refresh_token=None):
        """Represent a single authorization to Reddit's API.

        :param authenticator: An instance of a subclass of
            :class:`BaseAuthenticator`.
        :param refresh_token: (Optional) Enables the ability to refresh the
            authorization.

        """
        super(Authorizer, self).__init__(authenticator)
        self.refresh_token = refresh_token

    def authorize(self, code):
        """Obtain and set authorization tokens based on ``code``.

        :param code: The code obtained by an out-of-band authorization request
            to Reddit.

        """
        if self._authenticator.redirect_uri is None:
            raise InvalidInvocation('redirect URI not provided')
        self._request_token(code=code, grant_type='authorization_code',
                            redirect_uri=self._authenticator.redirect_uri)

    def refresh(self):
        """Obtain a new access token from the refresh_token."""
        if self.refresh_token is None:
            raise InvalidInvocation('refresh token not provided')
        self._request_token(grant_type='refresh_token',
                            refresh_token=self.refresh_token)

    def revoke(self, only_access=False):
        """Revoke the current Authorization.

        :param only_access: (Optional) When explicitly set to True, do not
            evict the refresh token if one is set.

        Revoking a refresh token will in-turn revoke all access tokens
        associated with that authorization.

        """
        if only_access or self.refresh_token is None:
            super(Authorizer, self).revoke()
        else:
            self._authenticator.revoke_token(self.refresh_token,
                                             'refresh_token')
            self._clear_access_token()
            self.refresh_token = None


class DeviceIDAuthorizer(BaseAuthorizer):
    """Manages app-only OAuth2 for 'installed' applications.

    While the '*' scope will be available, some endpoints simply will not work
    due to the lack of an associated Reddit account.

    """

    AUTHENTICATOR_CLASS = UntrustedAuthenticator

    def __init__(self, authenticator, device_id='DO_NOT_TRACK_THIS_DEVICE'):
        """Represent an app-only OAuth2 authorization for 'installed' apps.

        :param authenticator: An instance of :class:`UntrustedAuthenticator`.
        :param device_id: (optional) A unique ID (20-30 character ASCII string)
            (default DO_NOT_TRACK_THIS_DEVICE). For more information about this
            parameter, see:
            https://github.com/reddit/reddit/wiki/OAuth2#application-only-oauth
        """
        super(DeviceIDAuthorizer, self).__init__(authenticator)
        self._device_id = device_id

    def refresh(self):
        """Obtain a new access token."""
        grant_type = 'https://oauth.reddit.com/grants/installed_client'
        self._request_token(grant_type=grant_type,
                            device_id=self._device_id)


class ImplicitAuthorizer(BaseAuthorizer):
    """Manages implicit installed-app type authorizations."""

    AUTHENTICATOR_CLASS = UntrustedAuthenticator

    def __init__(self, authenticator, access_token, expires_in, scope):
        """Represent a single implicit authorization to Reddit's API.

        :param authenticator: An instance of :class:`UntrustedAuthenticator`.
        :param access_token: The access_token obtained from Reddit via callback
            to the authenticator's redirect_uri.
        :param expires_in: The number of seconds the ``access_token`` is valid
            for. The origin of this value was returned from Reddit via callback
            to the authenticator's redirect uri. Note, you may need to subtract
            an offset before passing in this number to account for a delay
            between when Reddit prepared the response, and when you make this
            function call.
        :param scope: A space-delimited string of Reddit OAuth2 scope names as
            returned from Reddit in the callback to the authenticator's
            redirect uri.

        """
        super(ImplicitAuthorizer, self).__init__(authenticator)
        self._expiration_timestamp = time.time() + expires_in
        self.access_token = access_token
        self.scopes = set(scope.split(' '))


class ReadOnlyAuthorizer(Authorizer):
    """Manages authorizations that are not associated with a Reddit account.

    While the '*' scope will be available, some endpoints simply will not work
    due to the lack of an associated Reddit account.

    """

    AUTHENTICATOR_CLASS = TrustedAuthenticator

    def refresh(self):
        """Obtain a new ReadOnly access token."""
        self._request_token(grant_type='client_credentials')


class ScriptAuthorizer(Authorizer):
    """Manages personal-use script type authorizations.

    Only users who are listed as developers for the application will be
    granted access tokens.

    """

    AUTHENTICATOR_CLASS = TrustedAuthenticator

    def __init__(self, authenticator, username, password):
        """Represent a single personal-use authorization to Reddit's API.

        :param authenticator: An instance of :class:`TrustedAuthenticator`.
        :param username: The Reddit username of one of the application's
            developers.
        :param password: The password associated with ``username``.

        """
        super(ScriptAuthorizer, self).__init__(authenticator)
        self._username = username
        self._password = password

    def refresh(self):
        """Obtain a new personal-use script type access token."""
        self._request_token(grant_type='password', username=self._username,
                            password=self._password)
