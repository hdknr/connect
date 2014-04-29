# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


_IDENTIFIER = dict(
    max_length=250,
    unique=True,
    db_index=True,
)


class AbstractAuthority(models.Model):
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    auth_metadata = models.TextField()      #: For OpenID Connect
    policy_metadata = models.TextField()    #: For UMA Core

    def __unicode__(self):
        return self.identifier

    class Meta:
        abstract = True


class AbstractRelyingParty(models.Model):
    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
    authority = models.ForeignKey(
        'Authority',
        related_name='%(app_label)s_%(class)s_related')
    metadata = models.TextField()

    def __unicode__(self):
        return self.identifier

    class Meta:
        abstract = True


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

    request = models.TextField()
    response = models.TextField()
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


#################################
#
#
#class AbstractResource(models.Model):
#    identifier = models.CharField(_(u'Identifier'), **_IDENTIFIER)
#    server = models.ForeignKey('Server')
#    scopes = models.ManyToManyField('Scope')
#
#    class Meta:
#        abstract = True
#
#
#class AbstractProtection(models.Model):
#    ''' Per Resoruce Owner' protection on Resrouce '''
#    token = models.ForeignKey('Token')
#    ''' Per User Protecteion API Token  '''
#    resource = models.ForeignKey('Resource')
#    scope = models.CharField(max_length=300,)   # Copy of Scope
#    # uri
#
#    class Meta:
#        abstract = True
#
#
##################################
#
#
#class AbstractConsumer(models.Model):
#    client = models.ForeignKey('Client')
#    token = models.ForeignKey('Token')  # Authorization API Token
#
#    class Meta:
#        abstract = True
#
#
#class AbstractRequest(models.Model):
#    consumer = models.ForeignKey('Consumer')
#    token = models.ForeignKey('Token')  # Requesting Party Token
#    resource = models.ForeignKey('Resource')
#    # server, resource and endpoint
#
#    class Meta:
#        abstract = True
