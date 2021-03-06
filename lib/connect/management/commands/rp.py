# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from . import GenericCommand, SubCommand

from connect.rp.models import SignOn, RelyingParty, Authority
from connect.messages.token import TokenRes
from connect.messages.id_token import IdToken
from connect.messages.auth import AuthRes
from connect.api.userinfo import UserInfoClient
from connect.api.token import TokenByCodeClient


from jose.base import JoseException

from optparse import make_option
import os
import traceback
import requests


class Command(GenericCommand):

    class PartyList(SubCommand):
        name = 'list_party'
        description = _(u'List Relying Party Command')

        def run(self, params, **options):
            for rp in RelyingParty.objects.all():
                print rp.id, rp.identifier, rp.authority
    
    class PartyDescription(SubCommand):
        name = 'desc_party'
        description = _(u'Detail of Party Command')
        args = [
            (('id',), dict(nargs=1, type=int, help="RelyingParty id")),
        ]

        def run(self, params, **options):
            
            print params
            print "Relying Party", "ID=", params.id[0]
            rp = RelyingParty.objects.get(id=int(params.id[0]))
            print rp.identifier
            print rp.authority
            print rp.reg_object.to_json(indent=2)
            
            print "Authority", "ID=", rp.authority.id
            print rp.authority.identifier
            print rp.authority.auth_metadata_object.to_json(indent=2)


    class AuthorityCreate(SubCommand):
        name = 'create_az'
        description = _(u'Create Authority')
        args = [
            (('vender',), 
             dict(nargs=1,
                  help="vender module path(connect.venders.google)")),
            (('tenant',), 
             dict(nargs='?',
                  help="Some vender requires tenant name")),
        ]

        def run(self, params, **options):
            mod = import_module(params.vender[0] + ".settings")
            func = "create_authority"
            return getattr(mod, func)(params.tenant, *args, **options)

    class AuthorityKeyUpdate(SubCommand):
        name = 'update_az_key'
        description = _(u'Update Authority Public Key')
        args = [
            (('id',), dict(nargs=1, type=int, help="Authority id")),
        ]
    
        def run(self, params, **options):
            id = params.id[0]
            try:
                az = Authority.objects.get(id=id)
                az.update_key()
                for key in az.keys.all():
                    print key and key.key_object.to_json(indent=2) 
    
            except Exception, ex:
                print traceback.format_exc()
                
                for authority in Authority.objects.all():
                    print authority.id, authority

    class AuthorityKeyList(SubCommand):
        name = 'list_az_key'
        description = _(u'List Authority Public Key')
        args = [
            (('id',), dict(nargs=1, type=int, help="Authority id")),
        ]
    
        def run(self, params, **options):
            for key in Authority.objects.get(id=params.id[0]).keys.all():
                print key.id
                print key.owner
                print key.jwkset.to_json(indent=2)

    class SignOnList(SubCommand):
        name = 'list_signon'
        description = _(u'List of SignOn')
        args = [
            (('queries',), dict(nargs='+', help="SignOn Queries k1=v1 k2=v2 ...")),
        ]
    
        def run(self, params, **options):
            query = dict( q.split('=') for q in params.queries )
            for signon in SignOn.objects.filter(**query):
                print so.id, so.party, so.nonce, so.state

    class SignOnDescription(SubCommand):
        name = 'desc_signon'
        description = _(u'List of SignOn')
        args = [
            (('id',), dict(nargs=1, type=int, help="SignOn id")), 
        ]
    
        def run(self, params, **options):
            signon = SignOn.objects.get(id=params.id[0])
            id_token_string = signon.get_id_token_string() 

            # TODO: SIOP routeine should be moved somewhere else
            if signon.authority.vender == "connect.venders.self":
                print "SIOP"
                id_token = IdToken.parse_siop_token(id_token_string)
                signon.verified = id_token.verified
                signon.id_token_object = id_token
                signon.save()
                print id_token.to_json(indent=2)

            print "*** Tokens ****"
            for token in signon.rp_token_related.all():
                print token.id, token.created_at , token.token


    class SignOnAuthRes(SubCommand):
        name = 'authres_signon'
        description = _(u'AuthRes to SignOn')
        args = [
            (('id',), dict(nargs=1, type=int, help="SignOn id")), 
            (('uri',), dict(nargs=1, type=str, help="AuthRes URI(GET)")), 
        ]
    
        def run(self, params, **options):
            signon = SignOn.objects.get(id=params.id[0])
            session_key = signon.session_key 
            if session_key is None:
                print "Session Key is not recorded."
                return

            if os.path.isfile(params.uri[0]):
                uri = open(params.uri[0]).read().rstrip('\n\r') 
            else:
                uri = params.id[0] 

            res = requests.get(uri) 
            print res.status_code


    class IdTokenDescription(SubCommand):
        name = 'desc_idtoken'
        description = _(u'Description of the ID Token for a SignOn')
        args = [
            (('id',), dict(nargs=1, type=int, help="SignOn id")), 
        ]
        def run(self, params, **options):
            so = SignOn.objects.get(id=params.id[0])
            res = TokenRes.from_json(so.tokens)
            id_token_str = res.id_token
            id_token_header = IdToken.header(id_token_str)
            jwk = id_token_header.load_key(so.authority)  
            print "Party:", so.party.id, so.party
            print "Authoryt:", so.party.authority.id, so.party.authority
            print "Token Header:", id_token_header and id_token_header.to_json(indent=2)
            print "Key :", jwk and jwk.to_json(indent=2) 
             
            try:
                so = SignOn.objects.get(id=params.id[0])
                print so.id_token_object.to_json(indent=2)
                print "JWT is  verified:", so.id_token_object.verified
            except JoseException, ex:
                print ex.message
                print ex.jobj and ex.jobj.to_json()
                print ex.args

    class UserInfoGet(SubCommand):
        name = 'get_userinfo'
        description = _(u'Get UserInfo with access token for a SignOn')
        args = [
            (('id',), dict(nargs=1, type=int, help="SignOn id")), 
        ]
        def run(self, params, **options):
            userinfo = UserInfoClient().call(
                SignOn.objects.get(id=params.id[0])) 
            print userinfo.to_json(indent=2)


    class TokenGet(SubCommand):
        name = 'get_token'
        description = _(u'Get Tokens with `code` for a SignOn')
        args = [
            (('id',), dict(nargs=1, type=int, help="SignOn id")), 
        ]
        def run(self, params, **options):
            token = TokenByCodeClient().code(
                SignOn.objects.get(id=params.id[0])) 

            print token.to_json(indent=2)

