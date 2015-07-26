# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from views import default, req, grant

urlpatterns = patterns(
    '',
    url(r'(?:(?P<tenant>.*)/)?api/', include('connect.az.api')),
    url(r'(?:(?P<tenant>.*)/)?tos', req, name='az_tos'),
    url(r'(?:(?P<tenant>.*)/)?policy', grant, name='az_policy'),
    url(r'(?:(?P<tenant>.*)/)?req', req, name='az_req'),
    url(r'(?:(?P<tenant>.*)/)?$', default, name='az_default'),
)
