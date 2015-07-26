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

from hashlib import sha1
from tastypie.http import HttpUnauthorized

from connect.api.auth import ConnectAuth
from connect.az.models import RelyingParty
from connect.api.auth import ConnectAuth

class ClientSecretBasic(ConnectAuth):
    """ Basic Authentication
    """
    def __init__(self, backend=None, realm='django-tastypie', **kwargs):
        super(ClientSecretBasic, self).__init__(**kwargs)
        self.realm = realm

    def _unauthorized(self):
        response = HttpUnauthorized()
        # FIXME: Sanitize realm.
        response['WWW-Authenticate'] = 'Basic Realm="%s"' % self.realm
        return response

    def is_authenticated(self, request, **kwargs):
        """
        """
        if not request.META.get('HTTP_AUTHORIZATION'):
            return self._unauthorized()

        try:
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
            if auth_type.lower() != 'basic':
                return self._unauthorized()
            user_pass = base64.b64decode(data).decode('utf-8')
        except:
            return self._unauthorized()

        try: 
            uid, pwd = user_pass.split(':')
            self.party = RelyingParty.objects.get(
                identifier=uid,
                secret=pwd,
            )     
            return True
        except ValueError:
            return self._unauthorized()
        except RelyingParty.DoesNotExist:
            return False 

    def get_identifier(self, request):
        """
        """
        return self.party and self.party.identifier
