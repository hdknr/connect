# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from connect.messages.discovery import ProviderMeta
from connect.messages.reg import ClientMeta, ClientReg
from connect.messages.auth import AuthReq, AuthRes
from connect.messages.token import TokenResCode, TokenRes
from connect.messages.id_token import IdToken
from connect.messages.userinfo import UserInfo
from jose.jwk import JwkSet, Jwk
import requests
import traceback
import re
from datetime import datetime
import pytz
import time

_IDENTIFIER = dict(
    max_length=250,
    unique=True,
    db_index=True,
)

_RELATION = '%(app_label)s_%(class)s_related'
_JSON_FIELD = re.compile('^(?P<name>.+)_object$')
_EPOCH_TIME = re.compile('^(?P<name>.+)_epoch$')


class BaseModel(models.Model):
    _serializer = {}
    
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    def find_serializer_name(self, name):
        _name = _JSON_FIELD.search(name)
        return _name and _name.groupdict()['name'] or None

    def __getattr__(self, name):
        _name = self.find_serializer_name(name)
        if _name:
            val = getattr(self, _name)
            return val and self._serializer[_name].from_json(val) or None

        _name = _EPOCH_TIME.search(name) 
        _val = _name and getattr(self, _name.groupdict()['name'])
        if _val and isinstance(_val, datetime):
            return int(time.mktime(_val.astimezone(pytz.utc).timetuple()))

        return self.__getattribute__(name)
    
    def __setattr__(self, name, value):
        _name = self.find_serializer_name(name)
        if _name:
            if value:
                setattr(self, _name, value.to_json(indent=2))
            else:
                setattr(self, _name, None) 
        else:
            super(BaseModel, self).__setattr__(name, value) 

    class Meta:
        abstract = True


class AbstractKey(BaseModel):
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

    _serializer = dict(key=Jwk)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s %s %s" % (
            self.owner.__unicode__(),
            self.jku or '',
            self.kid or '',
            self.x5t or '')  


class KeyOwner(BaseModel):

    def save_object(self, obj, uri, *args, **kwargs):
        for jwk in obj.keys:
            key, created = self.keys.get_or_create(
                owner=self, jku=uri, kid=jwk.kid, x5t=jwk.x5t)
            key.key_object = jwk
            key.save()

    def load_object(self, obj_class, uri, kid=None, x5t=None, *args, **kwargs):
        try:
            q = dict([(k, v) for k, v in dict(uri=uri, kid=kid, x5t=x5t).items() if v ])
            keys = [k.key_object for k in self.keys.filter(**q)]
            ret = JwkSet(keys=keys)
            return ret
        except:
            return None

    class Meta:
        abstract = True


class AbstractAuthority(KeyOwner):
    tenant = models.CharField(
        _(u'Tenant'), default=None,
       max_length=50, blank=True, null=True, db_index=True,)

    short_name = models.CharField(_(u'Name'), max_length=50)  #, unique=True,db_index=True)
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    auth_metadata = models.TextField(default='{}')      #: For OpenID Connect

    _serializer = dict(auth_metadata=ProviderMeta)

    def __unicode__(self):
        return self.short_name

    class Meta:
        abstract = True

    @classmethod
    def get_selfissued(cls):
        authority, created = cls.objects.get_or_create(
            identifier=ProviderMeta.selfissued_issuer)
        return authority

    def update_key(self):
        # TODO: SSL ann verify certificate.
        jku = self.auth_metadata_object.jwks_uri  
        if jku:
            res = requests.get(jku)
            jwkset = JwkSet.from_json(res.content)
            self.save_object(jwkset, jku)


class AbstractRelyingParty(KeyOwner):
    short_name = models.CharField(_(u'Name'), max_length=50)  #, unique=True,db_index=True)
    identifier = models.CharField(
        _(u'Identifier'), max_length=250, db_index=True)

    authority = models.ForeignKey('Authority', related_name=_RELATION)
    auth_metadata = models.TextField(default='{}')
    reg = models.TextField(_(u'Client Registration'), default='{}')
    auth_settings = models.TextField(_(u'Authentication Settings'), default='{}')

    _serializer = dict(auth_metadata=ClientMeta, reg=ClientReg)

    def __unicode__(self):
        return self.authority.__unicode__() + " " + self.short_name

    class Meta:
        abstract = True


class AbstractPreference(models.Model):
    ''' Authentication Preference managed by per User'''
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)
    user = models.ForeignKey(User, related_name=_RELATION)    
    preferences =  models.TextField(default='')

    class Meta:
        abstract = True


class AbstractIdentity(BaseModel):
    authority = models.ForeignKey('Authority', related_name=_RELATION)
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)

    subject = models.CharField(
        _(u'Subject'), max_length=200)

    user = models.ForeignKey(User, related_name=_RELATION)

    signon = models.ForeignKey(
        'SignOn', related_name=_RELATION,
        null=True, blank=True, default=None, on_delete=models.SET_NULL)

    id_token = models.TextField(default='{}')
    userinfo = models.TextField(default='{}')

    _serializer = dict(id_token=IdToken, userinfo=UserInfo)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s" % (
            self.party and self.party.__unicode__() or '',
            self.subject or ''
        )


class AbstractSignOn(BaseModel):
    authority = models.ForeignKey('Authority', related_name=_RELATION)
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)

    subject = models.CharField(
        _(u'Subject'), max_length=200,
        null=True, blank=True, default=None,)

    user = models.ForeignKey(
        User, related_name=_RELATION,
        null=True, blank=True, default=None)

    identity = models.ForeignKey(
        'Identity', related_name=_RELATION,
        null=True, blank=True, default=None)

    nonce = models.CharField(
        _('Nonce'), max_length=200, db_index=True, unique=True)

    state = models.CharField(
        _('State'), max_length=200, db_index=True, unique=True)

    verified = models.BooleanField(default=False)
    request = models.TextField(default='{}')
    response = models.TextField(default='{}')
    tokens = models.TextField(default='{}')
    id_token = models.TextField(default='{}')
    userinfo = models.TextField(default='{}')
    errors = models.TextField(default='{}')

    _serializer = dict(
        request=AuthReq, response=AuthRes, tokens=TokenRes,
        id_token=IdToken, userinfo=UserInfo)


    def __unicode__(self):
        return "%s(%s)" % (
            self.identity and self.identity.__unicode__() or "signon",
            self.id or "",
        )

    @property
    def identities(self):
        return self.party.rp_identity_related.filter(subject=self.subject)

    @property
    def access_token(self):
        token_response = self.tokens_object
        return token_response and token_response.access_token

    def get_id_token(self):
        token_response = self.tokens_object
        if token_response:
            id_token = IdToken.parse(
                token_response.id_token,
                sender=self.authority,
                recipient=self.party)
            self.id_token_object = id_token 
            self.save()
            return id_token     # has "verified" fields
        return None

    def bind_identity(self, user):
        if self.user and self.user != user:
            raise Exception("Swapped user")

        self.identity, created =  self.party.rp_identity_related.get_or_create(
            authority=self.authority,
            party =self.party,
            subject=self.subject,
            user=user)

        self.identity.signon = self
        self.identity.id_token = self.id_token
        self.identity.userinfo = self.userinfo
        self.identity.save()

        self.user = user
        self.save()

    class Meta:
        abstract = True


class AbstractScope(BaseModel):
    scope = models.CharField(
        _(u'Scope'), max_length=250, unique=True,)

    class Meta:
        abstract = True


class AbstractToken(BaseModel):
    signon = models.ForeignKey('SignOn', related_name=_RELATION)
    token_hash = models.CharField(max_length=100)
    token = models.TextField()
    scopes = models.ManyToManyField('Scope', related_name=_RELATION)

    class Meta:
        abstract = True
