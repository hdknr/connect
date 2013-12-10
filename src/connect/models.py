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
