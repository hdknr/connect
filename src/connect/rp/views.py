# -*- coding: utf-8 -*-
#from django.core.urlresolvers import reverse
from django.http import HttpResponse
#from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from forms import AuthReqForm
from connect.rp.models import (
    RelyingParty, SignOn
)
from connect.messages.auth import AuthReq


def default(request):
    return TemplateResponse(
        request,
        'rp/req.html',
        dict(request=request,
             form=AuthReqForm()))


def req(request):

    form = AuthReqForm(data=request.POST or None)
    if request.method == 'POST':
        if request.POST.get('submit-self'):
            return req_self(request)
        print request.POST

    return TemplateResponse(
        request,
        'rp/req.html',
        dict(request=request,
             form=form))


def req_self(request):
    uri = request.build_absolute_uri(reverse('rp_authres_self'))
    rp = RelyingParty.get_selfissued(uri)
    id_token_hint = None        # TODO

    authreq = AuthReq(
        response_type="id_token",
        redirect_uri=uri,
        registration=rp.auth_metadata,
        scope='openid',
        id_token_hint=id_token_hint,
        claims=None,
    )

    signon = SignOn.create(rp, authreq)
    assert signon is not None

    location = "openid://?" + authreq.to_qs()
    print "@@@@@", location

    res = HttpResponse(location, status=302)
    res['Location'] = location
    return res


def res_code(request):
    return TemplateResponse(
        request,
        'rp/res_code.html',
        dict(request=request))


def res_implicit(request):
    return TemplateResponse(
        request,
        'rp/res_implicit.html',
        dict(request=request))


def res_hybrid(request):
    return TemplateResponse(
        request,
        'rp/res_hybrid.html',
        dict(request=request))


def res_self(request):
    return TemplateResponse(
        request,
        'rp/res_self.html',
        dict(request=request))
