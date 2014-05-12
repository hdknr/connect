# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from connect.models import (
    AbstractKey,
    AbstractAuthority,
    AbstractRelyingParty,
    AbstractPreference,
    AbstractIdentity,
    AbstractSignOn,
    AbstractScope,
    AbstractToken,
)


class Authority(AbstractAuthority):

    class Meta:
        unique_together = (('identifier', 'tenant'), )

    @property
    def openid_configuration(self):
        meta = super(Authority, self).openid_configuration
        meta.issuer = self.identifier
        if self.tenant:
            meta['tenant'] = self.tenant
        return meta


class AuthorityKey(AbstractKey):
    owner = models.ForeignKey(Authority, related_name="keys")

    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class RelyingParty(AbstractRelyingParty):
    pass


class RelyingPartyKey(AbstractKey):
    owner = models.ForeignKey(RelyingParty, related_name="keys")
    class Meta:
        unique_together = (('jku', 'kid', 'x5t'), )


class Preference(AbstractPreference):

    class Meta:
        verbose_name = _(u'Relying Paryt Preference')
        verbose_name_plural = _(u'Relying Paryt Preferences')


class Identity(AbstractIdentity):
    pass


class SignOn(AbstractSignOn):
    pass


class Scope(AbstractScope):
    pass


class Token(AbstractToken):
    pass


#class Client(RelyingParty):
#    pass
#
#
#class Server(RelyingParty):
#    pass

#class Authority(AbstractAuthority):
#    class Meta:
#        verbose_name = _(u'OpenID Provider')
#        verbose_name_plural = _(u'OpenID Provider')
#
#
#class Client(AbstractClient):
#    authority = models.ForeignKey(Authority)
#
#    class Meta:
#        verbose_name = _(u'Resource Client')
#        verbose_name_plural = _(u'Resource Clients')
#
#
#class Server(AbstractServer):
#    authority = models.ForeignKey(Authority)
#
#    class Meta:
#        verbose_name = _(u'Resource Server')
#        verbose_name_plural = _(u'Resource Server')

#class Scope(models.Model):
#    server=  models.ForeignKey(Server)
#    name =  models.CharField(_(u'Scope'),
#                    max_length=100,db_index=True,unique=True)
#    description = models.TextField(_(u'Scope Description'),)
#    class Meta:
#        verbose_name = _(u'OAuth Scope')
#        verbose_name_plural = _(u'OAuth Scopes')
#
#class Resource(models.Model):
#    server = models.ForeignKey(Server)
#    scopes = models.ManyToManyField(Scope)
#    uri_hash = models.CharField(_('Resource Uri Hash'),
#                    max_length = 50,db_index=True,unique=True)
#    uri = models.TextField(_('Resource Uri'))
#
#    class Meta:
#        verbose_name = _(u'OAuth Protected Resource')
#        verbose_name_plural = _(u'OAuth Protected Resources')
#
#class Session(AbstractIdToken):
#    provider = models.ForeignKey(Provider)
#    client   = models.ForeignKey(Client)
#    user     = models.ForeignKey(User,related_name="servers_session_set")
#    class Meta:
#        verbose_name = _(u'OpenID Session')
#        verbose_name_plural = _(u'OpenID Session')
#
#class Access(models.Model):
#    session = models.ForeignKey(Session)
#    clients = models.ManyToManyField(Client)
#    resources = models.ManyToManyField(Resource)
#
#    token_hash = models.CharField(_(u'Access Token Hash'),
#                    max_length=50,db_index=True,unique=True)
#    token   =  models.TextField(_(u'Access Token'))
#
#    class Meta:
#        verbose_name = _(u'Access Token')
#        verbose_name_plural = _(u'Access Token')
