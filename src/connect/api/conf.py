from . import SingletonResource, ObjectSerializer
from connect.messages.meta import ProviderMeta


class ConfResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'openid-configuration'
        object_class = ProviderMeta
        serializer = ObjectSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        return ProviderMeta(issuer="me")
