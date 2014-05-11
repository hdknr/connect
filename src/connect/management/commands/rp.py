# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.rp.models import SignOn, Key, RelyingParty, Authority
from jose.base import JoseException

class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_party_list(self, *args, **option):
        for rp in RelyingParty.objects.all():
            print rp.id, rp.identifier, rp.authority

    def command_party(self, id, *args, **option):
        rp = RelyingParty.objects.get(id=int(id))
        print "Relying Party", "ID=", id
        print rp.identifier
        print rp.authority
        print rp.credentials.to_json(indent=2)
        
        print "Authority", "ID=", id
        print rp.authority.id
        print rp.authority.identifier
        print rp.authority.openid_configuration.to_json(indent=2)

    def command_update_auhority_keyset(self, id, *args, **options):
        try:
            az = Authority.objects.get(id=id)
            az.update_key()
            for key in az.keys.all():
                print key.to_json(indent=2) 

        except Exception, ex:
            print traceback.format_exc()

    def command_id_token(self, id, keyid=None , *args, **options):
        print "keyid ---", keyid
        try:
            so = SignOn.objects.get(id=id)
            print so.id_token.to_json()
        except JoseException, ex:
            print ex.message
            print ex.jobj and ex.jobj.to_json()
            print ex.args

        
        
