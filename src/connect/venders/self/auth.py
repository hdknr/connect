# -*- coding: utf-8 -*-
'''
Self Issued OP
https://openid.net/specs/openid-connect-core-1_0.html#SelfIssued
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
from connect.rp.views import save_signon, bind, request_token

from connect.messages.auth import AuthReq, AuthResCode, AuthRes
from settings import create_authority, create_relyingparty 

from jose.base import JoseException
import traceback

SCOPES = ["profile", "email", ]
PROMPT = ["none", "consent", "select_account",]

def req_any(request, vender, action, mode):
    # redirect_uri == client_id (7.2)
    ruri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
            vender='self', action='res', mode='implicit',
        ))
    )

    # TODO: create the Authority(=SIOP) if not created yet.
    authority = create_authority()

    # TODO: create the RP for SIOP if not created yet.
    rp = create_relyingparty(authority, ruri)

    form = AuthReqForm(
        vender=__package__,
        data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        rp = form.cleaned_data['rp']
        conf = rp.authority.auth_metadata_object

        # AuthReq (7.3)
        scopes = ["openid", "profile", "email", "address", "phone"]
        authreq = AuthReq(
            scope=" ".join(scopes),     # TODO: Selection 
            response_type="id_token",   # ID Token in implicit
            client_id=ruri,             # redirect_uri == client_id (7.2)
            id_token_hint=None,         
            claims=None,                
            registration=None,          # Client Meta
            request=None,               # Request Object
        )

        signon = SignOn.create(request.user, rp, authreq)
        request.session['state'] = signon.state

        if conf.authorization_endpoint.find('?') > 0:
            sep = "&"
        else:
            sep = "?"

        location = conf.authorization_endpoint + sep + authreq.to_qs()
        res = HttpResponse(location, status=302)
        res['Location'] = location
        return res

    ctx = dict(
        request=request, 
        vender=vender,
        form=form)

    return TemplateResponse(
        request,
        'venders/%s/req_any.html' % vender, ctx)


def res_implicit(request, vender, action, mode):
    '''
    '''
    authres = AuthRes.from_url(request.get_full_path())
    valid_state = authres.state == request.session['state']
    if not valid_state:
        raise Exception("Invalid State")

    signon = None
    errors = None
    try:
        signon = SignOn.objects.get(state=authres.state)
        signon.response_object = authres
        signon.save()

        if authres.error:
            raise Exception("authres error")

        id_token = request_token(
            request, signon, vender)

        save_signon(request, signon)
        return bind(request, signon)

    except Exception, ex:
        errors = traceback.format_exc()
        if signon:
            signon.errors = errors
            signon.save()
    
    
    ctx = dict(
            request=request,
            signon=signon,
            authres=authres,
            tokenres=signon.tokens_object,
            errors=errors,
    )

    return TemplateResponse(
        request, 'venders/self/res_error.html', ctx)
