from . import SingletonResource, ObjectSerializer
from connect.messages.discovery import ProviderMeta
from connect.az.models import Authority
import requests
import urlparse
from django.core.urlresolvers import reverse
import traceback


class ConfResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'openid-configuration'
        object_class = ProviderMeta
        serializer = ObjectSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        iss = bundle.request.build_absolute_uri('/%s' % (tenant or ''))

        try:
            authority, created = Authority.objects.get_or_create(
                identifier=iss, tenant=tenant)
            if created:
                # TODO: set default provider meta and save model
                # TODO: , if authomaticall create provider.
                pass

            ret = authority.openid_configuraiion

            ret.authorization_endpoint = urlparse.urljoin(
                ret.issuer, reverse('az_req'))
        except:
            print traceback.format_exc()

        return ret

class ConfClient(object):
    def call(self, server, **kwargs):
        return self.get(ConfResource.url(server, **kwargs))

    def get(self, uri):
        r = requests.get(
            uri, headers={"Accept": 'application/json'})
        return ProviderMeta.from_json(r.content)
