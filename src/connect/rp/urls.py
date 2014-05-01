# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from views import (
    default,
    auth,
    #    req, req_vender,
    #    res_code, res_code_vender,
    #    res_implicit, res_implicit_vender,
    #    res_hybrid, res_self,
)

_AUTH = r"(?:(?P<vender>.*)/)?auth/(?P<action>.+)/(?P<mode>.*)$"

urlpatterns = patterns(
    '',
    url(_AUTH, auth, name='rp_auth'),
    #    url(r'auth/res/self', res_self, name='rp_authres_self'),
    #    url(r'auth/res/hybrid', res_hybrid, name='rp_authres_hybrid'),
    #    url(r'auth/res/implicit/(?P<vender>.+)',
    #        res_implicit_vender, name='rp_authres_implicit_vender'),
    #    url(r'auth/res/implicit', res_implicit, name='rp_authres_implicit'),
    #    url(r'auth/res/code/(?P<vender>.+)',
    #        res_code_vender, name='rp_authres_code_vender'),
    #    url(r'auth/res/code', res_code, name='rp_authres_code'),
    #    url(r'auth/req/self', req, name='rp_authreq_self'),
    #    url(r'auth/req/(?P<vender>.+)', req_vender, name='rp_authreq_vender'),
    #    url(r'auth/req', req, name='rp_authreq'),
    url(r'$', default, name='rp_default'),
)
