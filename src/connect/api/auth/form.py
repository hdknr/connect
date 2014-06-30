from __future__ import unicode_literals
import base64
import hmac
import time
import uuid 
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import _sanitize_token, constant_time_compare
from django.utils.translation import ugettext as _

from tastypie.http import HttpUnauthorized
from connect.api.auth import ConnectAuth

from hashlib import sha1

from connect.az.models import RelyingParty
from connect.api.auth import ConnectAuth

import traceback

class ClientSecretPost(ConnectAuth):
    """ Client Form Authentication
    """
    def __init__(self, backend=None, realm='django-tastypie', **kwargs):
        super(ClientSecretPost, self).__init__(**kwargs)

    def is_authenticated(self, request, **kwargs):
        """
        """
        client_id = request.POST.get("client_id", None)
        client_secret = request.POST.get("client_id", None)

        if not all([client_id, client_secret]):
            return self._unauthorized()

        try: 
            self.party = RelyingParty.objects.get(
                identifier=client_id,
                secret=client_secret,
            )     
            return True
        except:
            return False 
         
        return True

    def get_identifier(self, request):
        """
        """
        return self.party and self.party.identifier


# - Abstract Message Flow
# Assertion Framework for OAuth 2.0 Client Authentication 
# and Authorization Grants
# http://tools.ietf.org/html/draft-ietf-oauth-assertions-16

# - Implementation 
# JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication 
# and Authorization Grants
# http://tools.ietf.org/html/draft-ietf-oauth-jwt-bearer-09


# Core 9.  Client Authentication  "client_secret_jwt"

class ClientSecretJwt(ClientSecretPost):
    client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"

    ''' Clients that have received a `client_secret` value 
        from the Authorization Server create a JWT using an HMAC SHA algorithm, 
        such as HMAC SHA-256. 
        
        The HMAC (Hash-based Message Authentication Code) is calculated 
        using the octets of the UTF-8 representation of the `client_secret` as the shared key.

        The Client authenticates in accordance with JSON Web Token (JWT) Profile for 
        OAuth 2.0 Client Authentication and 
        Authorization Grants [OAuth.JWT] and 
        Assertion Framework for OAuth 2.0 Client Authentication and 
        Authorization Grants [OAuth.Assertions]. 
    '''

    def get_assertion(self, request):
        param = type('',(),
                     dict((key, request.POST.get(key, None) 
                     for key in 
                     ('client_id', 
                      'client_assertion_type', 'client_assertion'))

        try:
            setattr(param, 'party',
                    param.client_id and RelyingParty.objects.get(client_id=param.client_id))
        except:
            setattr(param, 'party', None)
            pass
         
        return param, all([param.client_id, 
                    param.client_assertion_type == self.client_assertion_type,
                    param.client_asserton, param.party ]):

    def verify_assertion(self, param): 
        #: verify Jwt with Shared Jwk(kty='oct')
        return False 

    def is_authenticated(self, request, **kwargs):
        """
        """
        param, is_valid = self.get_assertion(request)
        if not is_valid:
            return self._unauthorized()
        
        try: 
            return self.verif_assertion(param)
        except:
            return False 
         
        return True

# Core 9.  Client Authentication  "private_key_jwt2

class PrivateKeyJwt(ClientSecretJwt):
    ''' Clients that have registered a public key sign a JWT using that key. 

        The Client authenticates in accordance 
        with JSON Web Token (JWT) Profile for 
        OAuth 2.0 Client Authentication and 
        Authorization Grants [OAuth.JWT] and 
        Assertion Framework for OAuth 2.0 Client Authentication and 
        Authorization Grants [OAuth.Assertions]. 
    '''
    def verify_assertion(self, param): 
        #: verify Jwt with Public Jwk(kty='RSA|EC')
        return False 

