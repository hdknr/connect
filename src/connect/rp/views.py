# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from importlib import import_module

from forms import AuthReqForm


def default(request):
    return TemplateResponse(
        request,
        'rp/core/req_any.html',
        dict(request=request,
             form=AuthReqForm()))


def auth(request, vender, action, mode):
    mod = import_module("connect.rp.%s" % vender or "core")
    func = "%s_%s" % (action, mode or "any")
#    print "@@@@@@@", vender, action, mode
    return getattr(mod, func)(request)
