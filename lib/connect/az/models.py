# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from connect import models as abstracts


class Authority(abstracts.Authority):

    class Meta:
        unique_together = (('identifier', 'tenant'), )


class AuthorityKey(abstracts.Key):
    owner = models.ForeignKey(Authority, related_name="keys")

    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class RelyingParty(abstracts.RelyingParty):
    pass


class RelyingPartyKey(abstracts.Key):
    owner = models.ForeignKey(RelyingParty, related_name="keys")

    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class Preference(abstracts.Preference):

    class Meta:
        verbose_name = _(u'Relying Paryt Preference')
        verbose_name_plural = _(u'Relying Paryt Preferences')


class Identity(abstracts.Identity):
    pass


class SignOn(abstracts.SignOn):
    pass


class Scope(abstracts.Scope):
    pass


class Token(abstracts.Token):
    pass
