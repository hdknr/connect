# -*- coding: utf-8 -*-
#from django.core.urlresolvers import reverse
from django.http import HttpResponse
#from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from connect.rp.models import (
    RelyingParty, SignOn
)
from connect.messages.auth import AuthReq


def req_any(request):
    print "@@@@@@", request.method
    if request.method == 'POST':
        uri = request.build_absolute_uri(
            reverse('rp_auth', kwargs=dict(
                vender='self', action='res', mode='implicit',
            ))
        )
        print "@@@@@", uri

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

        # HttpResponseRedirect DOES NOT WORK
        res = HttpResponse(location, status=302)
        res['Location'] = location
        return res

    return TemplateResponse(
        request,
        'rp/self/req_any.html',
        dict(request=request))


def res_implicit(request):
    return TemplateResponse(
        request,
        'rp/self/res_implicit.html',
        dict(request=request))
