from jose.jwt import Jwt
from jose.utils import merged

_id_token_fields = dict(
    auth_time=None,     # Authenticated Time
    nonce=None,         # Nonce(REQURIED for Implicit)
    acr=None,           # Authentication Context Class Reference
    amr=None,           # Authentication Methods References
    azp=None,           # Authorized party
    at_hash=None,       # Access Token hash value(REQUIRED for Implicit)
)


class IdToken(Jwt):
    _fields = merged([
        Jwt._fields,
        _id_token_fields,
    ])

    def __init__(self, *args, **kwargs):
        super(IdToken, self).__init__(*args, **kwargs)

if __name__ == '__main__':

    t = IdToken(nonce="this_is_nonce")
    assert t.nonce == 'this_is_nonce'
