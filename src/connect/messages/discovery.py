from jose import BaseObject


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

    selfissued_issuer = "https://self-issued.me"
