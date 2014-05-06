# -*- coding: utf-8 -*-
#from django.core.urlresolvers import reverse
#from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
#from django.core.urlresolvers import reverse

from connect.rp.forms import AuthReqForm
#from connect.rp.models import (
#    RelyingParty, SignOn
#)
#from connect.messages.auth import AuthReq


def req_any(request):

    form = AuthReqForm(data=request.POST or None)
    if request.method == 'POST':
        print request.POST

    return TemplateResponse(
        request,
        'venders/core/req_any.html',
        dict(request=request,
             form=form))


def res_code(request):
    return TemplateResponse(
        request,
        'venders/core/res_code.html',
        dict(request=request))


def res_implicit(request):
    return TemplateResponse(
        request,
        'venders/core/res_implicit.html',
        dict(request=request))


def res_hybrid(request):
    return TemplateResponse(
        request,
        'venders/core/res_hybrid.html',
        dict(request=request))
