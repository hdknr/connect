# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.rp.models import SignOn
from jose.base import JoseException

class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_id_token(self, id, *args, **options):
        try:
            so = SignOn.objects.get(id=id)
            print so.id_token.to_json()
        except JoseException, ex:
            print ex.message
            print ex.jobj and ex.jobj.to_json()
            print ex.args
