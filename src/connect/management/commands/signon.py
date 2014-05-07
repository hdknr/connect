# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.rp.models import SignOn


class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_id_token(self, id, *args, **options):
        so = SignOn.objects.get(id=id)
        print so.id_token.to_json()
