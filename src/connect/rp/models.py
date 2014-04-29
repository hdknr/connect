# -*- coding: utf-8 -*-
#from django.db import models
#from django.utils.translation import ugettext_lazy as _

from ..models import (
    AbstractAuthority,
    AbstractRelyingParty,
    AbstractIdentity,
    AbstractSignOn,
    AbstractScope,
    AbstractToken,
)


class Authority(AbstractAuthority):
    pass


class RelyingParty(AbstractRelyingParty):
    pass


class Identity(AbstractIdentity):
    pass


class SignOn(AbstractSignOn):
    pass


class Scope(AbstractScope):
    pass


class Token(AbstractToken):
    pass
