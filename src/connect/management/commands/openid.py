# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.api.finger import FingerClient
from connect.api.conf import ConfClient


class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_finger(self, server, resource, rel, *args, **options):
        jrd = FingerClient().call(server, resource, rel)
        print "Subject:", jrd.subject
        print "Link:", jrd.links[0].href
        print jrd.to_json()

    def command_conf(self, server, tenant=None, *args, **options):
        meta = ConfClient().call(server, tenant=tenant)
        print meta.to_json(indent=2)
