from tastypie.resources import Resource
from tastypie.serializers import Serializer
from django.conf.urls import url
from django.core.urlresolvers import reverse
import urlparse


class SingletonResource(Resource):
    formats = ['json', 'jrd']
    content_types = {
        'json': 'application/json',
        'jrd': 'application/jrd+json',
    }

    @classmethod
    def url_name(cls):
        return "%s_detail" % cls.Meta.resource_name

    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(
                r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, ''),
                self.wrap_view('dispatch_detail'),
                name=self.url_name())
        ]

    @classmethod
    def url(cls, host='', *args, **kwargs):
        kwargs['resource_name'] = cls.Meta.resource_name
        return urlparse.urljoin(host, reverse(cls.url_name(), kwargs=kwargs))


class ObjectSerializer(Serializer):
    def to_json(self, data, options=None):
        return data.obj.to_json()

    def to_jrd(self, data, options=None):
        return data.obj.to_json()
