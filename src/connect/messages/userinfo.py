from jose.base import BaseObject
from jose.utils import merged


_userinfo_fields = dict(
    sub=None, 
    email=None,
)

class UserInfo(BaseObject):
    _fields = _userinfo_fields
