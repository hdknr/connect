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

class ClientFormAuth(ConnectAuth):
    """ Form Authentication
    """
    def __init__(self, backend=None, realm='django-tastypie', **kwargs):
        super(ClientFormAuth, self).__init__(**kwargs)
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

        client_id = request.POST.get("client_id", None)
        client_secret = request.POST.get("client_id", None)

        if not all(client_id, client_secret):
            return self._unauthorized()

        try: 
            self.party = RelyingParty.objects.get(
                identifier=client_id,
                secret=client_secret,
            )     
            return True
        except RelyingParty.DoesNotExist:
            return False 

    def get_identifier(self, request):
        """
        """
        return self.party and self.party.identifier
