# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.translation import ugettext_lazy as _

from ..models import *

class Provider(AbstractProviderMeta):
    name = models.CharField(_(u'Provider Name'),max_length=20,db_index=True, unique=True)
    ''' distinguish name for multi tenant providers '''

    class Meta:
        verbose_name = _(u'OpenID Provider')
        verbose_name_plural = _(u'OpenID Provider')

class Client(AbstractClientMeta):
    provider = models.ForeignKey(Provider )
    class Meta:
        verbose_name = _(u'OpenID Client')
        verbose_name_plural = _(u'OpenID Client')

class Server(models.Model):
    identifier= models.CharField(_(u'Resouce Server Identifier'),
                        max_length=100,unique=True) 
    class Meta:
        verbose_name = _(u'Resource Server')
        verbose_name_plural = _(u'Resource Server')

class Scope(models.Model):
    server=  models.ForeignKey(Server)
    name =  models.CharField(_(u'Scope'),
                    max_length=100,db_index=True,unique=True)
    description = models.TextField(_(u'Scope Description'),)
    class Meta:
        verbose_name = _(u'OAuth Scope')
        verbose_name_plural = _(u'OAuth Scopes')

class Resource(models.Model):
    server = models.ForeignKey(Server)
    scopes = models.ManyToManyField(Scope)
    uri_hash = models.CharField(_('Resource Uri Hash'), 
                    max_length = 50,db_index=True,unique=True)
    uri = models.TextField(_('Resource Uri'))

    class Meta:
        verbose_name = _(u'OAuth Protected Resource')
        verbose_name_plural = _(u'OAuth Protected Resources')

class Session(AbstractIdToken):
    provider = models.ForeignKey(Provider) 
    client   = models.ForeignKey(Client)
    user     = models.ForeignKey(User) 
    class Meta:
        verbose_name = _(u'OpenID Session')
        verbose_name_plural = _(u'OpenID Session')

class Access(models.Model):
    session = models.ForeignKey(Session) 
    clients = models.ManyToManyField(Client) 
    resources = models.ManyToManyField(Resource) 
    
    token_hash = models.CharField(_(u'Access Token Hash'),
                    max_length=50,db_index=True,unique=True)
    token   =  models.TextField(_(u'Access Token')) 

    class Meta:
        verbose_name = _(u'Access Token')
        verbose_name_plural = _(u'Access Token')
