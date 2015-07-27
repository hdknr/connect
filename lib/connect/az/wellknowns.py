# -*- coding: utf-8 -*-
from django.conf.urls import url, include
# from connect.api import conf, finger

_pat = r'(?:(?P<tenant>.*)/)?.well-known/'
urlpatterns = [
    url(_pat, include('connect.rest.conf')),
    # url(_pat, include(finger.FingerResource().urls)),
]
