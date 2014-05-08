# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.rp.models import Authority
#from jose.base import JoseException
import traceback

class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_update_keyset(self, id, *args, **options):
        try:
            az = Authority.objects.get(id=id)
            az.update_key()
            for key in az.keys.all():
                print key.to_json(indent=2) 

        except Exception, ex:
            print traceback.format_exc()
