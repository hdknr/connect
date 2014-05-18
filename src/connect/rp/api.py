# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from connect.api import pubkey

urlpatterns = patterns(
    '',
    url(r'', include(pubkey.RelyingPartyKeyResource().urls)),
)
