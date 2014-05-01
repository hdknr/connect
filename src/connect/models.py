# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from connect.messages.discovery import ProviderMeta
from connect.messages.reg import ClientMeta, ClientReg
from connect.messages.auth import AuthReq, AuthResCode


_IDENTIFIER = dict(
    max_length=250,
    unique=True,
    db_index=True,
)


class AbstractKey(models.Model):
    owner = models.CharField(_(u'Owner'), max_length=200)
    uri = models.CharField(
        _(u'Uri'), max_length=200,
        null=True, blank=True, default=None)
    keyset = models.TextField(default='{}')

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.owner + " " + self.uri or ''


class KeyOwner(models.Model):
    keys = models.ManyToManyField(
        'Key', null=True, default=None, blank=True,
        related_name='%(app_label)s_%(class)s_related')

    def save_object(self, obj, uri, *args, **kwargs):
        key, created = self.keys.get_or_create(
            owner=self.__unicode__(),
            uri=uri)
        key.keyset = obj.to_json()

    def load_object(self, obj_class, uri, *args, **kwargs):
        try:
            return self.keys.get(
                owner=self.__unicode__(),
                uri=uri)
        except:
            return None

    class Meta:
        abstract = True


class AbstractAuthority(KeyOwner):
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


class AbstractRelyingParty(KeyOwner):
    identifier = models.CharField(
        _(u'Identifier'), max_length=250, db_index=True)

    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    auth_metadata = models.TextField(default='{}')
    reg = models.TextField(_(u'Client Registration'), default='{}')

    def __unicode__(self):
        return self.authority.identifier + " " + self.identifier

    class Meta:
        abstract = True

    @property
    def authmeta(self):
        return ClientMeta.from_json(self.auth_metadata)

    @authmeta.setter
    def authmeta(self, value):
        self.auth_metadata = value.to_json()

    @property
    def credentials(self):
        return ClientReg.from_json(self.reg)

    @credentials.setter
    def credentials(self, value):
        self.reg = value.to_json()


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

    @property
    def authreq(self):
        return AuthReq.from_json(self.request)

    @authreq.setter
    def authreq(self, value):
        self.request = value.to_json()

    @property
    def authres(self):
        # TODO : AuthResCode is vague
        return AuthResCode.from_json(self.request)

    @authres.setter
    def authres(self, value):
        self.response = value.to_json()

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
