# -*- coding: utf-8 -*-
#from django.core.urlresolvers import reverse
#from django.http.response import HttpResponseRedirect
#from django.http import HttpResponse
from django.template.response import TemplateResponse


def default(request, tenant=None):
    return TemplateResponse(
        request,
        'az/default.html',
        dict(request=request, tenant=tenant))


def req(request, tenant=None):
    return TemplateResponse(
        request,
        'az/req.html',
        dict(request=request, tenant=tenant))


def grant(request, tenant=None):
    return TemplateResponse(
        request,
        'az/grant.html',
        dict(request=request, tenant=tenant))
