# -*- coding: utf-8 -*-
'''
Google "OAuth 2.0 for Login(OpenID Connect)"
https://developers.google.com/accounts/docs/OAuth2Login
'''
from django.http import HttpResponse
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn
)
from connect.rp.views import save_signon, bind

from connect.messages.auth import AuthReq, AuthResCode, AuthRes

from jose.base import JoseException
import traceback

SCOPES = ["profile", "email", ]
PROMPT = ["none", "consent", "select_account",]

def req_any(request):
    form = AuthReqForm(
        vender=__package__,
        data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        rp = form.cleaned_data['rp']
        conf = rp.authority.openid_configuration

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
            scope="openid profile",
            prompt=PROMPT[1],
        )
        authreq['include_granted_scopes'] = 'false'

        signon = SignOn.create(request.user, rp, authreq)
        request.session['state'] = signon.state
        authreq.nonce = None            #: nonce not supported


        if conf.authorization_endpoint.find('?') > 0:
            sep = "&"
        else:
            sep = "?"

        location = conf.authorization_endpoint + sep + authreq.to_qs()
        res = HttpResponse(location, status=302)
        res['Location'] = location
        return res

    return TemplateResponse(
        request,
        'venders/google/req_any.html',
        dict(request=request, form=form))


def res_code(request):
    '''
    '''
    from requests.auth import HTTPBasicAuth
    import requests

    signons = SignOn.objects.filter(
        state=request.session['state'])

    signon = signons[0]     # TODO: check

    authres = AuthRes.from_url(request.get_full_path())
    signon.authres = authres
    signon.save()

    save_signon(request, signon)
    if authres.error:
        return TemplateResponse(
            request, 'venders/google/res_error.html', 
            dict(request=request, authres=authres))


    credentials = signon.party.credentials

    uri = signon.party.authority.openid_configuration.token_endpoint
    ruri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
            vender='google', action='res', mode='code',
        ))
    )
    data = dict(
        grant_type="authorization_code",
        code=request.GET.get('code'),
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        redirect_uri=ruri,
    )

    auth = HTTPBasicAuth(
        credentials.client_id,
        credentials.client_secret)

    res = requests.post(uri, data=data, auth=auth)
    signon.tokens = res.content
    signon.save()

    try:
        id_token = signon.id_token
    except JoseException, ex:
        print ex.message
        print ex.jobj.to_json()
        id_token = None

    if id_token:        
        signon.subject = id_token.sub
        if id_token.verified:
            signon.verified = True
            signon.save()

            return bind(request, signon)

    signon.save()

    ctx = RequestContext(
        request,dict(
            request=request,
            authres=authres,
            tokenres=signon.token_response,
    ))
    return TemplateResponse(
        request, 'venders/google/res_error.html', ctx)


