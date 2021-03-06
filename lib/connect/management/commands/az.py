# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from . import GenericCommand, SubCommand
from connect.az.models import (
    SignOn, RelyingParty, 
    Authority, AuthorityKey
)
from connect.messages.token import TokenRes
from connect.messages.id_token import IdToken
from connect.api.pubkey import AuthorityKeyResource
from jose.base import JoseException
from jose.jwk import Jwk, JwkSet
from optparse import make_option
import traceback


class Command(GenericCommand):

    class AuthorityCreate(SubCommand):
        name = 'create_az'
        description = _(u'Create Authority')
        args = [
            (('tenant',), 
             dict(nargs=1,
                  help="Distigush Name for Authority")),
            (('host',), 
             dict(nargs=1,
                  help="hostname (localhost:8000)")),
            (('scheme',), 
             dict(nargs='?',
                  help="scheme(default='https')")),
        ]

        def run(self, params, **options):
            authority, created = Authority.objects.get_or_create(
                identifier="%s://%s/%s" % (
                    params.scheme, params.host[0], params.tenant[0]),
                short_name=params.tenant[0],
                tenant=params.tenant[0],
            )

    class AuthorityList(SubCommand):
        name = 'list_az'
        description = _(u'List Authority')

        def run(self, parmas, **options):
            for authority in Authority.objects.all():
                print authority.id, authority

    class AuthorityDescription(SubCommand):
        name = 'desc_az'
        description = _(u'Description of Authority')
        args = [
            (('id',), 
             dict(nargs=1, type=int, help="Authority id")),
        ]

        def run(self, params, **options):
            print params.id
            authority = Authority.objects.get(id=params.id[0])
            print authority.id
            print authority.identifier 
            print authority.tenant

    class AuthorityCreateKey(SubCommand):
        name = 'create_az_key'
        description = _(u'Create Authority Key')
        args = [
            (('id',), 
             dict(nargs=1, type=int,
                  help="Authority id")),
            (('kty',), 
             dict(nargs=1, choices=['EC', 'RSA'],
                  help="Jwk Key Type(EC, RSA)")),
            (('--jkuid',), 
             dict(nargs='?', type=int,
                  help="Jku Optional Identifer")),
        ]

        def run(self, params, **options):
            authority  = Authority.objects.get(id=params.id[0])
            jku = authority.auth_metadata_object.jwks_uri or \
                AuthorityKeyResource.url(
                    authority.identifier, 
                    tenant=authority.tenant, id=params.jkuid)

            jwkset = JwkSet(
                keys=[Jwk.generate(kty=params.kty[0])])
            jwkset.save(authority, jku)

    class AuthorityActivateKey(SubCommand):
        name = 'activate_az_key'
        description = _(u'Activate (or Deactivate) Authority Key')
        args = [
            (('id',), 
             dict(nargs=1, type=int,
                  help="Authority Key id")),
            (('-off',), 
             dict(action='store_false', default=True, dest='on',
                  help="Activate or Deactivate")),
        ]

        def run(self, params, **options):
            AuthorityKey.objects.filter(
                id=params.id[0]).update(active=params.on)

    class AuthorityListKey(SubCommand):
        name = 'list_az_key'
        description = _(u'Create Authority Key')
        args = [
            (('id',), 
             dict(nargs=1, type=int,
                  help="Authority id")),
        ]

        def run(self, params, **options):
            for key in AuthorityKey.objects.filter(
                owner__id=params.id[0]):
                print "-----------"
                print key.id, key.jku, key.kid, key.x5t
                print key.key_object.to_json(indent=2)
                
    class AuthorityUpdateUri(SubCommand):
        name = 'update_az_uris'
        description = _(u'Update Authority Uris')
        args = [
            (('id',), 
             dict(nargs=1, type=int,
                  help="Authority id")),
            (('host',), 
             dict(nargs='?',
                  help="hostname (localhost:8000)")),
            (('scheme',), 
             dict(nargs='?',
                  help="scheme(default='https')")),
        ]

        def run(self, params, **options):
            print params.id, params.host, params.scheme

            authority = Authority.objects.get(id=params.id[0])
            authority.update_uris()
