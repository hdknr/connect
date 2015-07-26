from tastypie.resources import Resource
from tastypie.serializers import Serializer

from . import SingletonResource, ObjectSerializer
from .auth.bearer import OAuthBearer
from connect.messages.userinfo import UserInfo
import requests


class UserInfoResource(SingletonResource):

    class Meta:
        allowed_methods = ['get']
        resource_name = 'userinfo'
        object_class = UserInfo
        authentication = OAuthBearer(scopes=['openid'])
        serializer = ObjectSerializer(formats=['json'])

    def obj_get(self, bundle, tenant=None, *args, **kwargs):
        token = self._meta.authentication.token

        #: TODO: complete JSON
        userinfo = UserInfo(
            sub=token.signon.subject,
        )

        if token.scopes.filter(scope='email').exists():
            # TODO: fill email
            userinfo.email = "hoge@hoge.com"

        return userinfo

class UserInfoClient(object):
    def call(self, signon, **kwargs):
        token = signon.rp_token_related.order_by('-created_at')[0]
        uri = signon.authority.auth_metadata_object.userinfo_endpoint 
        return self.get_by_bearer(uri, token.token)

    def get_by_bearer(self, uri, token):
        r = requests.get(
            uri, headers={
                "Accept": 'application/json',
                "Authorization": "Bearer %s" % token, 
            })
        return UserInfo.from_json(r.content)
