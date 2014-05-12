# -*- coding: utf-8 -*-
'''
Google "OAuth 2.0 for Login(OpenID Connect)"
https://developers.google.com/accounts/docs/OAuth2Login
'''
from django.http import HttpResponse
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn
)
from connect.rp.views import save_signon, bind

from connect.messages.auth import AuthReq, AuthResCode, AuthRes

from jose.base import JoseException
import traceback


@login_required
def default(request, id, command):
    ctx = request,dict(
        request=request,
    )
    return TemplateResponse(
        request, 
        'venders/google/preference_detail.html',
        ctx)

@login_required
def items(request, id, command):
    ctx = request,dict(
        request=request,
    )
    return TemplateResponse(
        request, 
        'venders/google/preference_items.html',
        ctx)

@login_required
def edit(request, id, command):
    ctx = request,dict(
        request=request,
    )
    return TemplateResponse(
        request, 
        'venders/google/preference_edit.html',
        ctx)
