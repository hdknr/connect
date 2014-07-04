from tastypie.resources import Resource
from tastypie.serializers import Serializer
from tastypie.authentication import MultiAuthentication

from connect.messages.token import TokenRes
from connect.api import SingletonResource, ObjectSerializer
from connect.api.auth.form import ClientSecretPost
from connect.api.auth.basic import ClientSecretBasic

import requests

class TokenResource(SingletonResource):

    class Meta:
        allowed_methods = ['post',]
        resource_name = 'token'
        object_class = TokenRes
        always_return_data = True   # Important
        authentication = MultiAuthentication(
            ClientSecretPost(), ClientSecretBasic())
        serializer = ObjectSerializer(formats=['json'])

    def post_detail(self, request, **kwargs):
        print self._meta.authentication.party
        obj = TokenRes(access_token="xxx.......")
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)
        return self.create_response(request, bundle)


class TokenByCodeClient(object):
    def code(self, signon, **kwargs):
        uri = signon.authority.auth_metadata_object.token_endpoint
        form = dict(
            grant_type="authorization_code",
            code=signon.code,
            client_id=signon.party.identifier, 
            client_secret=signon.party.secret, 
            redirect_uri=signon.request_object.redirect_uri,
        )

        return self.post(uri, form)

    def post(self, uri, form):
        r = requests.post(
            uri, data=form,
            headers={
                "Accept": 'application/json',
            })
        return TokenRes.from_json(r.content)

