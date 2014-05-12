# -*- coding: utf-8 -*-
from django.utils.importlib import import_module

from . import GenericCommand
from connect.rp.models import SignOn, RelyingParty, Authority
from connect.messages.token import TokenRes
from connect.messages.id_token import IdToken
from jose.base import JoseException
from optparse import make_option
import traceback

class Command(GenericCommand):
    option_list = GenericCommand.option_list + (
         make_option('--id', '-i',
                     action='store',
                     dest='id',
                     default='utf-8',
                     help=u'model id'),
         make_option('--state', '-s',
                     action='store',
                     dest='state',
                     default='utf-8',
                     help=u'AuthReq state'),
         make_option('--nonce', '-n',
                     action='store',
                     dest='nonce',
                     default='utf-8',
                     help=u'nonce'),
    )

    def command_party_list(self, *args, **option):
        for rp in RelyingParty.objects.all():
            print rp.id, rp.identifier, rp.authority

    def command_party(self, id, *args, **option):
        rp = RelyingParty.objects.get(id=int(id))
        print "Relying Party", "ID=", id
        print rp.identifier
        print rp.authority
        print rp.credentials.to_json(indent=2)
        
        print "Authority", "ID=", rp.authority.id
        print rp.authority.identifier
        print rp.authority.openid_configuration.to_json(indent=2)

    def command_update_authority_keyset(self, id=None, *args, **options):
        try:
            az = Authority.objects.get(id=id)
            az.update_key()
            for key in az.keys.all():
                print key and key.jwkset.to_json(indent=2) 

        except Exception, ex:
            print traceback.format_exc()
            
            for authority in Authority.objects.all():
                print authority.id, authority

    def command_list_authorty_keyset(self, id=None, *args, **options):
        for key in Authority.objects.get(id=id).keys.all():
            print key.id
            print key.owner
            print key.jwkset.to_json(indent=2)

    def command_signon(self, *args, **options):

        for key in ['state', 'id', 'nonce',]:
           q = {} 
           if key in options:
                q[key] = options[key]
                so = SignOn.objects.get(**q)
                print so.id, so.party
                break 

    def command_id_token(self, id=None, keyid=None , *args, **options):
        so = SignOn.objects.get(id=id)
        res = TokenRes.from_json(so.tokens)
        id_token_str = res.id_token
        id_token_header = IdToken.header(id_token_str)
        jwk = id_token_header.load_key(so.authority)  
        print "Party:", so.party.id, so.party
        print "Authoryt:", so.party.authority.id, so.party.authority
        print "Token Header:", id_token_header and id_token_header.to_json(indent=2)
        print "Key :", jwk and jwk.to_json(indent=2) 
         
        
        try:
            so = SignOn.objects.get(id=id)
            print so.id_token.to_json()
            print "JWT is  verified:", so.id_token.verified
        except JoseException, ex:
            print ex.message
            print ex.jobj and ex.jobj.to_json()
            print ex.args

        
    def command_create_authority(self, vender, *args, **options):
        print vender
        mod = import_module(vender + ".settings")
        func = "create_authority"
        return getattr(mod, func)()
        
