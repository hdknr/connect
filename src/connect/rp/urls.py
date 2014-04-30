# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from views import (
    default, req,
    res_code, res_implicit, res_hybrid, res_self,
)

urlpatterns = patterns(
    '',
    url(r'auth/res/self', res_self, name='rp_authres_self'),
    url(r'auth/res/hybrid', res_hybrid, name='rp_authres_hybrid'),
    url(r'auth/res/implicit', res_implicit, name='rp_authres_implicit'),
    url(r'auth/res/code', res_code, name='rp_authres_code'),
    url(r'auth/req', req, name='rp_authreq'),
    url(r'$', default, name='rp_default'),
)
