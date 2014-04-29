from tastypie.resources import Resource
from tastypie.serializers import Serializer
#from django.core.serializers.json import DjangoJSONEncoder
#import json


class UserInfo(object):
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


class UserInfoSerializer(Serializer):
    def to_json(self, data, options=None):
        options = options or {}
        print type(data), data
        return "{}"


class UserInfoResource(Resource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'userinfo'
        object_class = UserInfo
        serializer = UserInfoSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        print "obj_get>>>>>", args, kwargs
        return UserInfo()

    def obj_get_list(self, bundle, tenant=None, *args, **kwargs):
        print "obj_get_list>>>>>", args, kwargs
        return [UserInfo()]