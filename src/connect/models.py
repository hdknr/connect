# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.translation import ugettext_lazy as _

import hashlib

# Abstract Model

class AbstractProviderMeta(models.Model):
    class Meta:
        verbose_name = _(u'Abstract OpenID Provider Metadata')
        verbose_name_plural = _(u'Abstract OpenID Provider Metadata')
        abstract =True

class AbstractClientMeta(models.Model):
    class Meta:
        verbose_name = _(u'Abstract OpenID Client Metadata')
        verbose_name_plural = _(u'Abstract OpenID Client Metadata')
        abstract =True

class AbstractIdToken(models.Model):
    class Meta:
        verbose_name = _(u'Abstract ID Token')
        verbose_name_plural = _(u'Abstract ID Token')
        abstract =True

class AbstractUserInfo(models.Model):
    class Meta:
        verbose_name = _(u'Abstract UserInfo')
        verbose_name_plural = _(u'Abstract UserInfo')
        abstract =True

# Concrete Model
class Provider(AbtractProviderMeta):
    name = models.CharField(_(u'Provider Name'),max_length=20,db_index=True, unique=True)
    ''' distinguish name for multi tenant providers '''
    class Meta:
        verbose_name = _(u'OpenID Provider')
        verbose_name_plural = _(u'OpenID Provider')

class RemoteProvider(AbtractProviderMeta):
    class Meta:
        verbose_name = _(u'Remote OpenID Provider')
        verbose_name_plural = _(u'Remote OpenID Provider')

class Client(AbtractClientMeta):
    provider = models.ForeignKey(RemoteProvider )
    class Meta:
        verbose_name = _(u'OpenID Client')
        verbose_name_plural = _(u'OpenID Client')

class RemoteClient(AbtractClientMeta):
    provider =  models.ForeignKey(Provider )
    class Meta:
        verbose_name = _(u'Remote OpenID Client')
        verbose_name_plural = _(u'Remote OpenID Client')

class RemoteSession(AbstractIdToken):
    provider = models.ForeignKey(Provider) 
    client   = modles.ForeignKey(RemoteClient)
    user     = models.ForeignKey(User) 
    class Meta:
        verbose_name = _(u'Remote Session')
        verbose_name_plural = _(u'Remote Session')

class Session(AbstractIdToken):
    provider = models.ForeignKey(RemoteProvider) 
    client   = modles.ForeignKey(Client)
    user     = models.ForeignKey(User) 
    class Meta:
        verbose_name = _(u'Session')
        verbose_name_plural = _(u'Session')
