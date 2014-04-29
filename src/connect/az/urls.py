# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from views import default, req, grant

urlpatterns = patterns(
    '',
    url(r'(?:(?P<tenant>.*)/)?api/', include('connect.api.urls')),
    url(r'(?:(?P<tenant>.*)/)?grant', grant, name='az_grant'),
    url(r'(?:(?P<tenant>.*)/)?req', req, name='az_req'),
    url(r'(?:(?P<tenant>.*)/)?$', default, name='az_default'),
)
