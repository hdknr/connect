# -*- coding: utf-8 -*-
from . import GenericCommand
from connect.api.finger import FingerResource
from connect.messages.finger import Jrd
import requests


class Command(GenericCommand):
    option_list = GenericCommand.option_list + ()

    def command_query(self, server, resource, rel, *args, **options):
        r = requests.get(
            FingerResource.url(server),
            params=dict(resource=resource, rel=rel),
            headers={"Accept": 'application/jrd+json'})
        jrd = Jrd.from_json(r.content)
        print "Subject:", jrd.subject
        print "Link:", jrd.links[0].href
        print jrd.to_json()
