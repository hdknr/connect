# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from connect.api import conf, finger

_pat = r'(?:(?P<tenant>.*)/)?.well-known/'
urlpatterns = patterns(
    '',
    url(_pat, include(conf.ConfResource().urls)),
    url(_pat, include(finger.FingerResource().urls)),
)
