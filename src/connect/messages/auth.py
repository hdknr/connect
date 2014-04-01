from jose import BaseObject
from jose.utils import merged


class AuthReq(BaseObject):
    _fields = dict(
        response_type=None,
        redirect_uri=None,
        nonce=None,
        scope=None,
        client_id=None,
        state=None,
        display=None,
        prompt=None,
        max_age=None,
        ui_locales=None,
        id_token_hint=None,
        login_hint=None,
        acr_values=None,
    )

_auth_res_code = dict(
    code=None,
    state=None,
)


class AuthResCode(BaseObject):
    _fields = _auth_res_code


class AuthResImplicit(BaseObject):
    _fields = dict(
        access_token=None,
        token_type=None,
        expires_in=None,
        scope=None,
        state=None,
    )


class AuthResHybrid(BaseObject):
    _fields = merged([
        AuthResCode._fields,
        dict(
            access_token=None,
            id_token=None,
            code=None,
        ),
    ])


class AuthResError(BaseObject):
    _fields = dict(
        error=None,
        error_description=None,
        error_uri=None,
        state=None,
    )
