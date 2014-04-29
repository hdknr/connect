from . import SingletonResource, ObjectSerializer
from connect.messages.discovery import ProviderMeta
import requests


class ConfResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'openid-configuration'
        object_class = ProviderMeta
        serializer = ObjectSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        ret = ProviderMeta(issuer="me")
        if tenant:
            ret['tenant'] = tenant
        return ret


class ConfClient(object):
    def call(self, server, **kwargs):
        r = requests.get(
            ConfResource.url(server, **kwargs),
            headers={"Accept": 'application/json'})
        return ProviderMeta.from_json(r.content)
