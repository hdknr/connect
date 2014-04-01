from jose import BaseObject
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


class ProviderMeta(BaseObject):
    ''' Discovery1.0 3.
    '''
    _fileds = dict(
        issuer=None,
        authorization_endpoint=None,
        token_endpoint=None,
        userinfo_endpoint=None,
        jwks_uri=None,
        registration_endpoint=None,
        scopes_supported=None,
        response_types_supported=None,
        response_modes_supported=None,
        grant_types_supported=None,
        acr_values_supported=None,
        subject_types_supported=None,
        id_token_signing_alg_values_supported=None,
        id_token_encryption_alg_values_supported=None,
        id_token_encryption_enc_values_supported=None,
        userinfo_signing_alg_values_supported=None,
        userinfo_encryption_alg_values_supported=None,
        userinfo_encryption_enc_values_supported=None,
        request_object_signing_alg_values_supported=None,
        request_object_encryption_alg_values_supported=None,
        request_object_encryption_enc_values_supported=None,
        token_endpoint_auth_methods_supported=None,
        token_endpoint_auth_signing_alg_values_supported=None,
        display_values_supported=None,
        claim_types_supported=None,
        claims_supported=None,
        service_documentation=None,
        claims_locales_supported=None,
        ui_locales_supported=None,
        claims_parameter_supported=None,
        request_parameter_supported=None,
        request_uri_parameter_supported=None,
        require_request_uri_registration=None,
        op_policy_uri=None,
        op_tos_uri=None,
    )
