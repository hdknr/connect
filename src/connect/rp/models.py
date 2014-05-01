# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from jose.utils import nonce, _BE
import hashlib

from ..models import (
    AbstractKey,
    AbstractAuthority,
    AbstractRelyingParty,
    AbstractIdentity,
    AbstractSignOn,
    AbstractScope,
    AbstractToken,
)

from connect.messages.reg import ClientMeta


class Key(AbstractKey):
    class Meta:
        unique_together = (('owner', 'uri'), )


class Authority(AbstractAuthority):
    vender = models.CharField(_(u'Vender'), max_length=50)
    pass


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


class SignOn(AbstractSignOn):
    nonce = models.CharField(
        _('Nonce'), max_length=200, db_index=True, unique=True)
    state = models.CharField(
        _('State'), max_length=200, db_index=True, unique=True)

    @classmethod
    def state_from_nonce(cls, nonce):
        return _BE(hashlib.sha256(nonce + settings.SECRET_KEY).digest())

    @classmethod
    def create(cls, party, authreq=None):
        n = nonce('S')
        s = cls.state_from_nonce(n)
        if authreq:
            authreq.nonce = n
            authreq.state = s

        signon = cls(
            authority=party.authority,
            party=party,
            nonce=n,
            state=s,
            request=authreq and authreq.to_json(),
        )
        signon.save()
        return signon


class Identity(AbstractIdentity):
    pass


class Scope(AbstractScope):
    pass


class Token(AbstractToken):
    pass
