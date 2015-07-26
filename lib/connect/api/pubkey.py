from . import SingletonResource, ObjectSerializer
from connect.az.models import Authority, AuthorityKey
from connect.rp.models import RelyingParty, RelyingPartyKey
import requests
import urlparse
from django.core.urlresolvers import reverse
from django.conf.urls import url
import traceback
from jose.jwk import JwkSet


class PublicKeyResource(SingletonResource):

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(
                r"^(?P<resource_name>%s)(?:/(?P<id>.*))?$" % (self._meta.resource_name, ),
                self.wrap_view('dispatch_detail'),
                name=self.url_name())
        ]

    def keyset(self, bundle, *args, **kwargs):
        raise NotImplemented()

    def obj_get(self, bundle, *args, **kwargs):
        try:
            return JwkSet(keyset=self.keyset(bundle, *args, **kwargs))
        except:
            return JwkSet()

    def jku(self, bundle, *args, **kwargs):
        return bundle.request.build_absolute_uri(bundle.request.path)

    class Meta:
        allowed_methods = ['get']
        object_class = JwkSet
        serializer = ObjectSerializer(formats=['json'])

class AuthorityKeyResource(PublicKeyResource):

    class Meta(PublicKeyResource.Meta):
        resource_name = 'azkey'

    def keyset(self, bundle, tenant=None, id=None, *args, **kwargs):
        jku = self.jku(bundle)
        return [key.key_object.public_jwk
                for key 
                in AuthorityKey.objects.filter(jku=jku, active=True,)]

class RelyingPartyKeyResource(PublicKeyResource):

    class Meta(PublicKeyResource.Meta):
        resource_name = 'rpkey'

    def keyset(self, bundle, tenant=None, id=None, *args, **kwargs):
        jku = self.jku(bundle)
        return [key.key_object.public_jwk 
                for key 
                in RelyingPartyKey.objects.filter(jku=jku, active=True,)]


class AuthorityKeyClient(object):
    def call(self, server, **kwargs):
        r = requests.get(
            AuthorityKeyResource.url(server, **kwargs),
            headers={"Accept": 'application/json'})
        print r.content
        return JwkSet.from_json(r.content)


class RelyingPartyKeyClient(object):
    def call(self, server, **kwargs):
        r = requests.get(
            RelyingPartyKeyResource.url(server, **kwargs),
            headers={"Accept": 'application/json'})
        print r.content
        return JwkSet.from_json(r.content)
