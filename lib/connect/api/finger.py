from . import SingletonResource, ObjectSerializer
from connect.messages.finger import Jrd, Link
import requests


class FingerResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'webfinger'
        object_class = Jrd
        serializer = ObjectSerializer(
            formats=['jrd'],
            content_types=dict(
                jrd=Jrd._media_type,
                json='application/json',
            )
        )

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        resource = bundle.request.GET.get('resource', None)
        rel = bundle.request.GET.get('rel', None)
        if resource and rel:
            #: TODO query resource and compose Jrd
            return Jrd(
                subject=resource,
                links=[Link(rel=rel,
                            type="https://hoge",
                            href="https://hoge.com")],
            )
        return Jrd()


class FingerClient(object):
    def call(self, server, resource, rel):
        r = requests.get(
            FingerResource.url(server),
            params=dict(resource=resource, rel=rel),
            headers={"Accept": 'application/jrd+json, application/json'})
        return Jrd.from_json(r.content)
