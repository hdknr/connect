# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from connect.messages.discovery import ProviderMeta
from connect.messages.reg import ClientMeta


_IDENTIFIER = dict(
    max_length=250,
    unique=True,
    db_index=True,
)


class AbstractAuthority(models.Model):
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    auth_metadata = models.TextField(default='{}')      #: For OpenID Connect

    def __unicode__(self):
        return self.identifier

    class Meta:
        abstract = True

    @classmethod
    def get_selfissued(cls):
        authority, created = cls.objects.get_or_create(
            identifier=ProviderMeta.selfissued_issuer)
        return authority

    @property
    def openid_configuration(self):
        return ProviderMeta.from_json(self.auth_metadata)

    @openid_configuration.setter
    def openid_configuration(self, value):
        self.auth_metadata = value.to_json()


class AbstractRelyingParty(models.Model):
    identifier = models.CharField(
        _(u'Identifier'), max_length=250, db_index=True)

    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    auth_metadata = models.TextField(default='{}')

    def __unicode__(self):
        return self.identifier

    class Meta:
        abstract = True

    @property
    def registration(self):
        return ClientMeta.from_json(self.auth_metadata)

    @registration.setter
    def registration(self, value):
        self.auth_metadata = value.to_json()


class AbstractIdentity(models.Model):
    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    party = models.ForeignKey(
        'RelyingParty',
        related_name='%(app_label)s_%(class)s_related')
    user = models.ForeignKey(
        User,
        related_name='%(app_label)s_%(class)s_related')

    subject = models.CharField(
        _(u'Subject'), max_length=200)

    class Meta:
        abstract = True


class AbstractSignOn(models.Model):
    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')

    party = models.ForeignKey(
        'RelyingParty',
        related_name='%(app_label)s_%(class)s_related')

    user = models.ForeignKey(
        User,
        related_name='%(app_label)s_%(class)s_related',
        null=True, blank=True, default=None)

    request = models.TextField(default='{}')
    response = models.TextField(default='{}')
#    assertion = models.TextField()      # ID Token

    class Meta:
        abstract = True


class AbstractScope(models.Model):
    scope = models.CharField(
        _(u'Scope'), max_length=250, unique=True,)

    class Meta:
        abstract = True


class AbstractToken(models.Model):
    signon = models.ForeignKey(
        'SignOn',
        related_name='%(app_label)s_%(class)s_related')
    token_hash = models.CharField(max_length=100)
    token = models.TextField()
    scopes = models.ManyToManyField(
        'Scope',
        related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True
