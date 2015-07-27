from jose.jwt import Jwt
from jose.jwk import Jwk
from jose.utils import merged
from jose.crypto import KeyOwner

_id_token_fields = dict(
    auth_time=None,     # Authenticated Time
    nonce=None,         # Nonce(REQURIED for Implicit)
    acr=None,           # Authentication Context Class Reference
    amr=None,           # Authentication Methods References
    azp=None,           # Authorized party
    at_hash=None,       # Access Token hash value(REQUIRED for Implicit)
    sub_jwk=None,       # Self Issued OP
)


class SiopSender(KeyOwner):
    def __init__(self, token):
        self.id_token = IdToken.from_b64u(token.split('.')[1])
        self.jwk = Jwk.from_json(self.id_token.sub_jwk)

    def get_key(self, crypto):
        return self.jwk


class IdToken(Jwt):
    _fields = merged([
        Jwt._fields,
        _id_token_fields,
    ])

    def __init__(self, *args, **kwargs):
        super(IdToken, self).__init__(*args, **kwargs)

    @classmethod
    def parse_siop_token(cls, token):
        # TODO: parse JWS Payload to extract sub_jwk
        #       create wrapper
        sender = SiopSender(token)
        return cls.parse(token, sender, None)

if __name__ == '__main__':

    t = IdToken(nonce="this_is_nonce")
    assert t.nonce == 'this_is_nonce'
