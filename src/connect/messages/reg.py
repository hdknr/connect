from jose.base import BaseObject
from jose.utils import merged


class ClientMeta(BaseObject):
    ''' Reg1.0  2.
    '''
    _fields = dict(
        redirect_uris=None,
        response_type=None,
        grant_types=None,
        application_type=None,
        contacts=None,
        client_name=None,
        logo_uri=None,
        client_uri=None,
        token_endpoint_auth_method=None,
        policy_uri=None,
        tos_uri=None,
        jwks_uri=None,
        jwks=None,
        sector_identifier_uri=None,
        subject_type=None,
        request_object_signing_alg=None,
        userinfo_signed_response_alg=None,
        userinfo_encrypted_response_alg=None,
        userinfo_encrypted_response_enc=None,
        id_token_signed_response_alg=None,
        id_token_encrypted_response_alg=None,
        id_token_encrypted_response_enc=None,
        default_max_age=None,
        require_auth_time=None,
        default_acr_values=None,
        initiate_login_uri=None,
        post_logout_redirect_uris=None,
        request_uris=None,
    )

_client_reg = dict(
    client_id=None,
    client_secret=None,
    registration_access_token=None,
    registration_client_uri=None,
    client_id_issued_at=None,
    client_secret_expires_at=None,
)


class ClientReg(BaseObject):
    _fields = merged([
        ClientMeta._fields,
        _client_reg,
    ])


class ClientRegError(BaseObject):
    _fields = dict(
        error=None,
        error_description=None,
    )
