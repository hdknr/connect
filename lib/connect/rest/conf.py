from django.core.urlresolvers import reverse
from django.conf.urls import url

from rest_framework.decorators import api_view
from furl import furl
import requests

from connect.messages.discovery import ProviderMeta
from connect.az.models import Authority


@api_view(['GET'])
def openid_configuration(request, tenant=None, *args, **kwargs):
    iss = request.build_absolute_uri('/%s' % (tenant or ''))
    authority, created = Authority.objects.get_or_create(
        identifier=iss, tenant=tenant)

    if created:
        # TODO: set default provider meta and save model
        # TODO: , if authomaticall create provider.
        pass

    ret = authority.openid_configuration

    ret.authorization_endpoint = furl(ret.issuer).join(reverse('az_req'))


urlpatterns = [
    url(r'^openid-configuration',
        openid_configuration, name="connect_openid_configuration"),
]


class ConfClient(object):

    def get(self, uri):
        r = requests.get(
            uri, headers={"Accept": 'application/json'})
        return ProviderMeta.from_json(r.content)
