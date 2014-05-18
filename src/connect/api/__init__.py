from tastypie.resources import Resource
from tastypie.serializers import Serializer
from django.conf.urls import url
from django.core.urlresolvers import reverse
import urlparse
import requests


class SingletonResource(Resource):
    formats = ['json', 'jrd']
    content_types = {
        'json': 'application/json',
        'jrd': 'application/jrd+json',
    }

    def get_context(self, request_type, request, **kwargs):
        ''' creating authentication context object
        '''
        return None

    def dispatch(self, request_type, request, **kwargs):
        ''' tastypie Resource#dipatch
        '''
        
        # provide requesting context to the authentication object
        self._meta.authentication.context = self.get_context(  
            request_type, request, **kwargs)

        # tastypie implementation
        return super(SingletonResource, self).dispatch(
            request_type, request, **kwargs)
            

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
        kwargs = dict(
            tuple([(k, v) for k, v in kwargs.items() if v is not None]))
        ret = urlparse.urljoin(host, reverse(cls.url_name(), kwargs=kwargs))
        return ret


class ObjectSerializer(Serializer):
    def to_json(self, data, options=None):
        return data.obj.to_json()

    def to_jrd(self, data, options=None):
        return data.obj.to_json()


class MessageClient(object):

    @classmethod
    def get(self, message_class, uri, ):
        r = requests.get(
            uri, headers={"Accept": 'application/json'})
        return message_class.from_json(r.content)
