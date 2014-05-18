# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from connect.models import (
    AbstractKey,
    AbstractAuthority,
    AbstractRelyingParty,
    AbstractPreference,
    AbstractIdentity,
    AbstractSignOn,
    AbstractScope,
    AbstractToken,
)


class Authority(AbstractAuthority):

    class Meta:
        unique_together = (('identifier', 'tenant'), )

class AuthorityKey(AbstractKey):
    owner = models.ForeignKey(Authority, related_name="keys")

    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class RelyingParty(AbstractRelyingParty):
    pass


class RelyingPartyKey(AbstractKey):
    owner = models.ForeignKey(RelyingParty, related_name="keys")
    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class Preference(AbstractPreference):

    class Meta:
        verbose_name = _(u'Relying Paryt Preference')
        verbose_name_plural = _(u'Relying Paryt Preferences')


class Identity(AbstractIdentity):
    pass


class SignOn(AbstractSignOn):
    pass


class Scope(AbstractScope):
    pass


class Token(AbstractToken):
    pass

