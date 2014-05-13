from jose.base import BaseObject
from jose.utils import merged


# OpenID Connect Core 1.0 
# 5.1.  Standard Claims

_userinfo_fields = dict(
    sub=None, 
    name=None,
    given_name=None,
    family_name=None,
    middle_name=None,
    nickname=None,
    preferred_username=None,
    email=None,
    profile=None,
    picture=None,
    website=None,
    email_verified=None,    # bool 
    gender=None,
    birthdate=None,
    zoneinfo=None,          # "Asia/Tokyo"
    locale=None,            # RFC5646
    phone_number=None,      # E.164
    phone_number_verified=None, # bool
    address=None,           # Address
    updated_at=None         # number
)


_address_fields = dict(
    formatted=None,
    street_address=None,
    locality=None,      # City or locality component
    region=None,        # State, province, prefecture, or region component
    postal_code=None,
    country=None,
)


class UserInfo(BaseObject):
    _fields = _userinfo_fields

    def __init__(self, *args, **kwargs):
        suepr(UserInfo, self).__init__(*args, **kwargs) 
        if isinstance(self.address, dict):
            self.address = Address(**self.address)


class Address(BaseObject):
    _fields = _address_fields
