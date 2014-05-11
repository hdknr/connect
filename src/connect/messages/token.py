from jose.base import BaseObject
from jose.utils import merged


class TokenReqCode(BaseObject):
    ''' OAuth 4.1.3
        Core 3.1.3.1
    '''
    _fields = dict(
        grant_type=None,
        code=None,
        redirect_uri=None,
        client_id=None,
    )


# OAuth 5.1
_oauth_token_res_code = dict(
    access_token=None,
    token_type=None,
    expires_in=None,
    refresh_token=None,
    scope=None,
)

_oauth_token_res_openid = dict(
    id_token=None,      # Core 3.1.3.3
)


# OAuth 5.2
_oauth_token_res_code_error = dict(
    error=None,
    error_description=None,
    error_uri=None,
)

_oauth_token_res_owner = dict(
    grant_type=None,    # "password",
    username=None,
    password=None,
    scope=None,
)

_oauth_token_res_client = dict(
    grant_type=None,     # "client_credentials"
    scope=None,
)

_oauth_token_res_refresh = dict(
    grant_type=None,    # "refresh_token",
    refresh_token=None,
    scope=None,
)


class TokenResCode(BaseObject):
    ''' OAuth 5.1 / Core 3.1.3.3
    '''
    _fields = merged([
        _oauth_token_res_code,
        _oauth_token_res_openid,
    ])


class TokenResCodeError(BaseObject):
    '''
    '''
    _fields = _oauth_token_res_code_error


class TokenReqOwner(BaseObject):
    ''' OAuth 4.3.2
    '''
    _fields = _oauth_token_res_owner


class TokenResOwner(BaseObject):
    _fields = _oauth_token_res_code



class TokenResOnwerError(TokenResCodeError):
    pass



class TokenReqClient(BaseObject):
    ''' OAuth 4.4.3
    '''
    _fields = _oauth_token_res_client

class TokenResClient(BaseObject):
    _fields = _oauth_token_res_code


class TokenResClientError(TokenResCodeError):
    pass


class TokenReqRefresh(BaseObject):
    ''' OAuth 6
    '''
    _fields = _oauth_token_res_refresh


class TokenResRefresh(BaseObject):
    _fields = _oauth_token_res_code


class TokenResRefreshError(TokenResCodeError):
    pass


class TokenRes(BaseObject):
    ''' Generi Token Response Json '''
    _fields = merged([
        _oauth_token_res_code,
        _oauth_token_res_owner,
        _oauth_token_res_openid,
        _oauth_token_res_client,
        _oauth_token_res_owner,
        _oauth_token_res_refresh,
        _oauth_token_res_code_error,
    ])
