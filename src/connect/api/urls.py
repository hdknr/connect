# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from . import userinfo, token, reg

urlpatterns = patterns(
    '',
    url(r'', include(reg.RegResource().urls)),
    url(r'', include(token.TokenResource().urls)),
    url(r'', include(userinfo.UserInfoResource().urls)),
)

