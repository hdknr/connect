# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from views import (
    default,
    auth,
    bind,
    signup,
    select,
    id_list,
    id_detail,
)

_AUTH = r"(?:(?P<vender>.*)/)?auth/(?P<action>.+)/(?P<mode>.*)$"

urlpatterns = patterns(
    '',
    url("id/(?P<id>\d+)", id_detail, name='rp_id_detail'),
    url("id", id_list, name='rp_id_lis'),
    url("bind", bind, name='rp_bind'),
    url("select", select, name='rp_select'),
    url("signup", signup, name='rp_signup'),
    url(_AUTH, auth, name='rp_auth'),
    url(r'$', default, name='rp_default'),
)
