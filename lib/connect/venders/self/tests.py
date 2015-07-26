'''
python manage.py test connect.venders.self.tests
'''

from django.test import TestCase
from django.conf import settings
from django.utils.importlib import import_module

import os

from connect.messages.auth import AuthRes


FIXTURES = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'fixtures')


class TestSiop(TestCase):

    fixtures = [""]

    def setUp(self):
        """
        set up sessions for anonymous users
        """
        from django.test import client
        from django.contrib import auth

        self.client = client.Client()
        self.user = auth.get_user(self.client)
        
        self.init_session()

    def init_session(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()    # new session data
        store.save()  # we need to make load() work, or the cookie is worthless
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_response(self):
        '''
        python manage.py test connect.venders.self.tests.TestSiop.test_response
        '''
        # TODO: this test only works when the AuthReq has been created..
        
        auth_res_path = None
        with open(os.path.join(FIXTURES, "res.txt")) as data:
            auth_res_path = data.read().rstrip('\r\n')

        self.assertIsNotNone(auth_res_path)

        authres = AuthRes.from_url(auth_res_path)

        session = self.client.session
        session['state'] = authres.state
        session.save()
       
        res = self.client.get(auth_res_path)
