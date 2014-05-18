from tastypie.resources import Resource
from tastypie.serializers import Serializer
from connect.api import SingletonResource
#from django.core.serializers.json import DjangoJSONEncoder
#import json


class Reg(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}
        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class RegSerializer(Serializer):
    def to_json(self, data, options=None):
        options = options or {}
        print type(data), data
        return "{}"


class RegResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'reg'
        object_class = Reg
        serializer = RegSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        print "Reg obj_get>>>>>", args, kwargs
        return Reg()

    def obj_get_list(self, bundle, tenant=None, *args, **kwargs):
        print "Reg obj_get_list>>>>> tenant = ", tenant, args, kwargs
        return [Reg()]
