# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import views

_AUTH = r"(?:(?P<vender>.*)/)?auth/(?P<action>.+)/(?P<mode>.*)$"

urlpatterns = patterns(
    '',
    url("conf/signon/(?P<id>\d+)", views.signon_detail, name='rp_signon_detail'),
    url("conf/az/(?P<id>\d+)", views.authority_detail, name='rp_authority_detail'),
    url("conf/id/(?P<id>\d+)", views.identity_detail, name='rp_identity_detail'),
    url("conf/id", views.identity_list, name='rp_identity_list'),
    url("conf/", views.conf_default, name='rp_conf_default'),
    url("bind", views.bind, name='rp_bind'),
    url("select", views.select, name='rp_select'),
    url("signup", views.signup, name='rp_signup'),
    url(_AUTH, views.auth, name='rp_auth'),
    url(r'$', views.default, name='rp_default'),
)
