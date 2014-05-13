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
from connect.rp.views import save_signon, bind, request_token

from connect.messages.auth import AuthReq, AuthResCode, AuthRes

from jose.base import JoseException
import traceback

SCOPES = ["profile", "email", ]
PROMPT = ["none", "consent", "select_account",]

def req_any(request, vender, action, mode):
    form = AuthReqForm(
        vender=__package__,
        data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        rp = form.cleaned_data['rp']
        conf = rp.authority.auth_metadata_object

        ruri = request.build_absolute_uri(
            reverse('rp_auth', kwargs=dict(
                vender='google', action='res', mode='code',
            ))
        )
        # https://developers.google.com/accounts/docs/OAuth2Login#authenticationuriparameters

        authreq = AuthReq(
            response_type="code",
            client_id=rp.identifier,
            redirect_uri=ruri,
            scope="openid profile email",
            prompt=PROMPT[1],
        )
        authreq['include_granted_scopes'] = 'false'

        signon = SignOn.create(request.user, rp, authreq)
        request.session['state'] = signon.state
        authreq.nonce = None            #: TODO: nonce not supported ?

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
        'venders/google/req_any.html', ctx)


def res_code(request, vender, action, mode):
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
        request, 'venders/google/res_error.html', ctx)

