# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from jose.utils import nonce, _BE
import hashlib

from ..models import (
    AbstractKey,
    AbstractAuthority,
    AbstractRelyingParty,
    AbstractPreference,
    AbstractIdentity,
    AbstractSignOn,
    AbstractScope,
    AbstractToken,
)

from connect.messages.reg import ClientMeta


class Authority(AbstractAuthority):
    vender = models.CharField(_(u'Vender'), max_length=50)

    class Meta:
        unique_together = (('identifier', 'tenant'), )


class AuthorityKey(AbstractKey):
    owner = models.ForeignKey(Authority, related_name="keys") 
    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )



class RelyingParty(AbstractRelyingParty):

    @classmethod
    def get_selfissued(cls, redirect_uri):
        rp, created = cls.objects.get_or_create(
            identifier=redirect_uri,
            authority=Authority.get_selfissued(),
        )
        if created:
            rp.registration = ClientMeta(
                redirect_uris=[redirect_uri],
            )
            rp.save()

        return rp

    class Meta:
        unique_together = (('identifier', 'authority'), )


class RelyingPartyKey(AbstractKey):
    owner = models.ForeignKey(RelyingParty, related_name="keys") 
    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class Preference(AbstractPreference):

    class Meta:
        verbose_name = _(u'Relying Party Preference')
        verbose_name_plural = _(u'Relying Party Preferences')


class SignOn(AbstractSignOn):

    @classmethod
    def state_from_nonce(cls, nonce):
        return _BE(hashlib.sha256(nonce + settings.SECRET_KEY).digest())

    @classmethod
    def create(cls, user, party, authreq=None):
        n = nonce('S')
        s = cls.state_from_nonce(n)
        if authreq:
            authreq.nonce = n
            authreq.state = s

        if isinstance(user, AnonymousUser):
            user = None

        signon = cls(
            authority=party.authority,
            party=party,
            nonce=n,
            state=s,
            user=user,
        )
        signon.request_object = authreq
        signon.save()
        return signon


class Identity(AbstractIdentity):
    pass


class Scope(AbstractScope):
    pass


class Token(AbstractToken):
    pass
