# -*- coding: utf-8 -*-
from . import GenericCommand, SubCommand
from django.utils.translation import ugettext_lazy as _

from connect.api.finger import FingerClient
from connect.api.conf import ConfClient
from connect.api import MessageClient
from jose.jwk import JwkSet


class Command(GenericCommand):

    class Finger(SubCommand):
        name = 'finger'
        description = _(u'WebFinger')
        args = [
            (('server',), dict(nargs=1,  help="Server to be queried.")),
            (('resource',), dict(nargs=1,  help="Resource Type")),
            (('rel',), dict(nargs=1,  help="Link Relation")),
        ]
        def run(self, params, **options):
            jrd = FingerClient().call(
                params.server[0], params.resource[0], params.rel[0])

            print "Subject:", jrd.subject
            print "Link:", jrd.links[0].href
            print jrd.to_json()

    
    class GetOpenIDConfiguration(SubCommand):
        name = 'conf'
        description = _(u'Get OpenID Configuration')
        args = [
            (('server',), dict(nargs=1,  help="OpenID OP")), 
            (('tenant',), dict(nargs='?',  help="teneant")), 
        ]
        def run(self, params, **options):
            meta = ConfClient().call(server, tenant=tenant)
            print meta.to_json(indent=2)

    class GetJwkSet(SubCommand):
        name = 'jwkset'
        description = _(u'Get JwkSet Public Key')
        args = [
            (('url',), dict(nargs=1,  help="Jku")), 
        ]
        def run(self, params, **options):
            jwkset = MessageClient.get(JwkSet, params.url[0])
            print jwkset.to_json(indent=2)
