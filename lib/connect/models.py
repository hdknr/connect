# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from connect import messages
from jose.jwk import JwkSet, Jwk
from jose.crypto import KeyOwner as JoseKeyOwner
import requests
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


class JsonField(models.TextField):
    def __init__(
        self, serializer=messages.BaseObject,
        defualt='{}', *args, **kwargs
    ):
        super(JsonField, self).__init__(*args, **kwargs)
        self.serializer = serializer

    def get_internal_type(self):
        return 'TextField'


class BaseModel(models.Model):
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True, )
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True, )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseModel, self).__init__(*args, **kwargs)

    def find_serializer_name(self, name):
        _name = _JSON_FIELD.search(name)
        return _name and _name.groupdict()['name'] or None

    def find_jsonfield(self, name):
        actual_name = self.find_serializer_name(name)
        return actual_name and self._meta.get_field(actual_name)

    def __getattr__(self, name):
        field = self.find_jsonfield(name)
        if field:
            val = getattr(self, field.name)
            return val and field.serializer.from_json(val) or None

        _name = _EPOCH_TIME.search(name)
        _val = _name and getattr(self, _name.groupdict()['name'])
        if _val and isinstance(_val, datetime):
            return int(time.mktime(_val.astimezone(pytz.utc).timetuple()))

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        field = self.find_jsonfield(name)
        if field:
            if value:
                setattr(self, field.name, value.to_json(indent=2))
            else:
                setattr(self, field.name, None)
        else:
            super(BaseModel, self).__setattr__(name, value)


class Key(BaseModel):
    jku = models.CharField(
        _(u'Jku'), max_length=200,
        null=True, blank=True, default=None)
    kid = models.CharField(
        _(u'Key ID'), max_length=100,
        null=True, blank=True, default=None)
    x5t = models.CharField(
        _(u'X.509 Thumprint'), max_length=100,
        null=True, blank=True, default=None)

    active = models.BooleanField(default=True)
    key = JsonField(serializer=Jwk)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s %s %s" % (
            self.owner.__unicode__(),
            self.jku or '',
            self.kid or '',
            self.x5t or '')


class KeyOwner(BaseModel, JoseKeyOwner):

    def get_key(self, crypto):
        ''' crypto: Jws, Jwe instance '''
        q = dict(
            [(k, v) for
             k, v in dict(
                uri=crypto.jku, kid=crypto.kid, x5t=crypto.x5t).items() if v])

        keys = [k.key_object for k in self.keys.filter(**q)]
        ret = JwkSet(keys=keys)
        return ret

    class Meta:
        abstract = True


class Authority(KeyOwner):
    tenant = models.CharField(
        _(u'Tenant'), default=None,
        max_length=50, blank=True, null=True, db_index=True,)

    short_name = models.CharField(_(u'Name'), max_length=50)
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    auth_metadata = JsonField(serializer=messages.ProviderMeta)

    def __unicode__(self):
        return self.short_name

    class Meta:
        abstract = True

    @classmethod
    def get_selfissued(cls):
        authority, created = cls.objects.get_or_create(
            identifier=messages.ProviderMeta.selfissued_issuer)
        return authority

    def update_key(self):
        # TODO: SSL ann verify certificate.
        jku = self.auth_metadata_object.jwks_uri
        if jku:
            res = requests.get(jku)
            jwkset = JwkSet.from_json(res.content)
            self.save_object(jwkset, jku)


class RelyingParty(KeyOwner):
    short_name = models.CharField(_(u'Name'), max_length=50)
    identifier = models.CharField(
        _(u'Identifier'), max_length=250, db_index=True)
    secret = models.CharField(
        _(u'Secret'), max_length=100, default=None, null=True, blank=True,)

    authority = models.ForeignKey('Authority', related_name=_RELATION)

    auth_metadata = JsonField(serializer=messages.ClientMeta)
    reg = JsonField(serializer=messages.ClientMeta)

    auth_settings = models.TextField(
        _(u'Authentication Settings'), default='{}')

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.authority.__unicode__() + " " + self.short_name


class Preference(models.Model):
    ''' Authentication Preference managed by per User'''
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)
    user = models.ForeignKey(User, related_name=_RELATION)
    preferences = models.TextField(default='')

    class Meta:
        abstract = True


class Identity(BaseModel):
    authority = models.ForeignKey('Authority', related_name=_RELATION)
    party = models.ForeignKey('RelyingParty', related_name=_RELATION)

    subject = models.CharField(_(u'Subject'), max_length=200)

    user = models.ForeignKey(User, related_name=_RELATION)

    signon = models.ForeignKey(
        'SignOn', related_name=_RELATION,
        null=True, blank=True, default=None, on_delete=models.SET_NULL)

    id_token = JsonField(serializer=messages.IdToken)
    userinfo = JsonField(serializer=messages.UserInfo)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s %s" % (
            self.party and self.party.__unicode__() or '',
            self.subject or ''
        )


class SignOn(BaseModel):
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

    session_key = models.CharField(
        _('Session Key'),
        max_length=200, db_index=True,
        null=True, blank=True, default=None)

    nonce = models.CharField(
        _('Nonce'), max_length=200, db_index=True, unique=True)

    state = models.CharField(
        _('State'), max_length=200, db_index=True, unique=True)

    code = models.CharField(
        _('Code'), max_length=100,
        db_index=True, null=True, blank=True,)

    verified = models.BooleanField(default=False)

    request = JsonField(serializer=messages.AuthReq)
    response = JsonField(serializer=messages.AuthRes)
    tokens = JsonField(serializer=messages.TokenRes)
    id_token = JsonField(serializer=messages.IdToken)
    userinfo = JsonField(serializer=messages.UserInfo)

    errors = models.TextField(default='{}')

    class Meta:
        abstract = True

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

    def get_id_token_string(self):
        token_response = self.tokens_object

        if token_response and token_response.id_token:
            return token_response.id_token

        #: Implicit Flow
        res = self.response_object
        return res and res.id_token or None

    def get_id_token(self):
        id_token_string = self.get_id_token_string()

        if not id_token_string:
            return None

        # IdToken object
        id_token = messages.IdToken.parse(
            id_token_string,
            sender=self.authority,
            recipient=self.party)

        self.id_token_object = id_token
        self.save()
        return self.id_token_object     # has "verified" fields

    def bind_identity(self, user):
        if self.user and self.user != user:
            raise Exception("Swapped user")

        self.identity, created = self.party.rp_identity_related.get_or_create(
            authority=self.authority,
            party=self.party,
            subject=self.subject,
            user=user)

        self.identity.signon = self
        self.identity.id_token = self.id_token
        self.identity.userinfo = self.userinfo
        self.identity.save()

        self.user = user
        self.save()


class Scope(BaseModel):
    scope = models.CharField(
        _(u'Scope'), max_length=250, unique=True,)
    authorities = models.ManyToManyField(
        'Authority', related_name=_RELATION)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.scope or "(scope)"


class Token(BaseModel):
    signon = models.ForeignKey('SignOn', related_name=_RELATION)
    token_hash = models.CharField(max_length=100)
    token = models.TextField()
    scopes = models.ManyToManyField('Scope', related_name=_RELATION)

    class Meta:
        abstract = True
