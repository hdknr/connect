from jose.base import BaseObject
from jose.utils import merged

# OAuth 2.0 Authentication Reuqest
# 4.1.1. Authorization Request
# http://tools.ietf.org/html/rfc6749.html#section-4.1.1

_auth_req_oauth = dict(
    scope=None,
    response_type=None,
    client_id=None,
    redirect_uri=None,
    state=None,
)

# OpenID Connet Extension
# 3.1.2.1. Authentication Request
_auth_req_connect = dict(
    response_mode=None,
    nonce=None,             # Copied to ID Token
    display=None,
    prompt=None,
    max_age=None,
    ui_locales=None,
    id_token_hint=None,
    login_hint=None,
    acr_values=None,
)

# 7.2.1. Providing Information
# with the "registration" Request Parameter
# - The value is a JSON object containing Client metadata values
_auth_req_selfissued = dict(
    registration=None,
)


class AuthReq(BaseObject):
    ''' Connect Core 1.0
    '''
    _fields = merged([
        _auth_req_oauth,
        _auth_req_connect,
        _auth_req_selfissued,
    ])


_auth_res_code = dict(
    code=None,
    state=None,
)

_auth_res_implicit = dict(
    access_token=None,
    token_type=None,
    expires_in=None,
    scope=None,
    state=None,
)

_auth_res_hybrid = dict(
    access_token=None,
    id_token=None,
    code=None,
)

_auth_res_error = dict(
    error=None,
    error_description=None,
    error_uri=None,
    state=None,
)

class AuthResCode(BaseObject):
    _fields = _auth_res_code


class AuthResImplicit(BaseObject):
    _fields = _auth_res_implicit


class AuthResHybrid(BaseObject):
    _fields = merged([
        AuthResCode._fields,
        AuthResImplicit._fields,
        _auth_res_hybrid,
    ])


class AuthResError(BaseObject):
    _fields = _auth_res_error


class AuthRes(BaseObject):
    _fields = merged([
        _auth_res_code,
        _auth_res_implicit,
        _auth_res_hybrid,
        _auth_res_error,
    ])
