# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from connect.messages.discovery import ProviderMeta
from connect.messages.reg import ClientMeta, ClientReg
from connect.messages.auth import AuthReq, AuthRes
from connect.messages.token import TokenResCode
from connect.messages.id_token import IdToken
from jose.jwk import JwkSet, Jwk
import requests
import traceback


_IDENTIFIER = dict(
    max_length=250,
    unique=True,
    db_index=True,
)

_RELATION = '%(app_label)s_%(class)s_related'


class AbstractKey(models.Model):
    jku = models.CharField(
        _(u'Jku'), max_length=200,
        null=True, blank=True, default=None)
    kid = models.CharField(
        _(u'Key ID'), max_length=100, 
        null=True, blank=True, default=None)
    x5t = models.CharField(
        _(u'X.509 Thumprint'), max_length=100, 
        null=True, blank=True, default=None)

    key = models.TextField(default='{}')

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True

    @property
    def jwk(self):
        return Jwk.from_json(self.key)

    @jwk.setter
    def jwk(self, value):
        self.key = value.to_json(indent=2)

    def __unicode__(self):
        return "%s %s %s %s" % (
            self.owner.__unicode__(),
            self.jku or '',
            self.kid or '',
            self.x5t or '')  



class KeyOwner(models.Model):
#    keys = models.ManyToManyField(
#        'Key', null=True, default=None, blank=True,
#        related_name='%(app_label)s_%(class)s_related')

    def save_object(self, obj, uri, *args, **kwargs):
        for jwk in obj.keys:
            key, created = self.keys.get_or_create(
                owner=self,
                jku=uri,
                kid=jwk.kid,
                x5t=jwk.x5t)
            key.key = jwk.to_json(indent=2)
            key.save()

    def load_object(self, obj_class, uri, kid=None, x5t=None, *args, **kwargs):
        try:
            q = dict([(k, v) for k, v in dict(uri=uri, kid=kid, x5t=x5t).items() if v ])
            keys = [k.jwk for k in self.keys.filter(**q)]
            ret = JwkSet(keys=keys)
            return ret
        except:
            return None

    class Meta:
        abstract = True


class AbstractAuthority(KeyOwner):
    short_name = models.CharField(_(u'Name'), max_length=50)  #, unique=True,db_index=True)
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    auth_metadata = models.TextField(default='{}')      #: For OpenID Connect

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    def __unicode__(self):
        return self.short_name

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
        self.auth_metadata = value.to_json(indent=2)

    def update_key(self):
        # TODO: SSL ann verify certificate.
        jku = self.openid_configuration.jwks_uri
        if jku:
            res = requests.get(jku)
            jwkset = JwkSet.from_json(res.content)
            self.save_object(jwkset, jku)

#;    def jwkset(self, jku=None):
#;        jku = jku or self.openid_configuration.jwks_uri
#;        return self.load_object(JwkSet, jku).jwkset


class AbstractRelyingParty(KeyOwner):
    short_name = models.CharField(_(u'Name'), max_length=50)  #, unique=True,db_index=True)
    identifier = models.CharField(
        _(u'Identifier'), max_length=250, db_index=True)

    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    auth_metadata = models.TextField(default='{}')
    reg = models.TextField(_(u'Client Registration'), default='{}')
    auth_settings = models.TextField(_(u'Authentication Settings'), default='{}')

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    def __unicode__(self):
        return self.authority.__unicode__() + " " + self.short_name

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



class AbstractPreference(models.Model):
    ''' Authentication Preference managed by per User'''
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)
    user = models.ForeignKey(User, related_name=_RELATION)    
    preferences =  models.TextField(default='')

    class Meta:
        abstract = True


class AbstractIdentity(models.Model):
    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    party = models.ForeignKey(
        'RelyingParty',
        related_name='%(app_label)s_%(class)s_related')

    subject = models.CharField(
        _(u'Subject'), max_length=200)

    user = models.ForeignKey(
        User,
        related_name='%(app_label)s_%(class)s_related')

    userinfo = models.TextField(default='{}')

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s" % (
            self.party and self.party.__unicode__() or '',
            self.subject or ''
        )


class AbstractSignOn(models.Model):
    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')

    party = models.ForeignKey(
        'RelyingParty',
        related_name='%(app_label)s_%(class)s_related')

    subject = models.CharField(
        _(u'Subject'), max_length=200,
        null=True, blank=True, default=None,)

    user = models.ForeignKey(
        User,
        related_name='%(app_label)s_%(class)s_related',
        null=True, blank=True, default=None)

    nonce = models.CharField(
        _('Nonce'), max_length=200, db_index=True, unique=True)

    state = models.CharField(
        _('State'), max_length=200, db_index=True, unique=True)

    verified = models.BooleanField(default=False)
    request = models.TextField(default='{}')
    response = models.TextField(default='{}')
    tokens = models.TextField(default='{}')
    errors = models.TextField(default='{}')

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    @property
    def authreq(self):
        return AuthReq.from_json(self.request)

    @authreq.setter
    def authreq(self, value):
        self.request = value.to_json(indent=2)

    @property
    def authres(self):
        return AuthRes.from_json(self.request)

    @authres.setter
    def authres(self, value):
        self.response = value.to_json(indent=2)

    @property
    def identities(self):
        return self.party.rp_identity_related.filter(subject=self.subject)

    @property
    def access_token(self):
        token_response = self.token_response
        return token_response and token_response.access_token

    @property
    def id_token(self):
        token_response = self.token_response
        if token_response:
            id_token = IdToken.parse(
                token_response.id_token,
                sender=self.authority,
                recipient=self.party)
            return id_token
        return None

    @property
    def token_response(self):
        if self.tokens:
            return TokenResCode.from_json(self.tokens)
        return None

    class Meta:
        abstract = True


class AbstractScope(models.Model):
    scope = models.CharField(
        _(u'Scope'), max_length=250, unique=True,)
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

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

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True
