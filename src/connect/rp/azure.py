# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn
)
from connect.messages.auth import AuthReq, AuthResCode
import json
from jose.utils import _BD
import traceback


def req_any(request):
    form = AuthReqForm(
        vender='connect.rp.azure',
        data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        rp = form.cleaned_data['rp']
        conf = rp.authority.openid_configuration

        ruri = request.build_absolute_uri(
            reverse('rp_auth', kwargs=dict(
                vender='azure', action='res', mode='code',
            ))
        )
        authreq = AuthReq(
            response_type="code",
            client_id=rp.identifier,
            redirect_uri=ruri,
            scope="openid profile",
            prompt="admin_consent",
        )
        authreq['resource'] = "https://graph.windows.net"

        signon = SignOn.create(rp, authreq)
        authreq['session_state'] = signon.state
        request.session['state'] = signon.state

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
        'rp/azure/req_any.html',
        dict(request=request,
             form=form))


def res_code(request):
    '''
    '''
    from requests.auth import HTTPBasicAuth
    import requests

    signons = SignOn.objects.filter(
        state=request.session['state'])

    signon = signons[0]     # TODO: check
    signon.authres = AuthResCode.from_url(request.get_full_path())
    signon.save()

    credentials = signon.party.credentials

    uri = signon.party.authority.openid_configuration.token_endpoint
    uri = "https://login.windows.net/common/oauth2/token"
    ruri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
            vender='azure', action='res', mode='code',
        ))
    )
    data = dict(
        #       grant_type="client_credentials",
        grant_type="authorization_code",
        code=request.GET.get('code'),
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        #        session_state=request.GET.get('session_state'),
        resource="https://graph.windows.net",
        redirect_uri=ruri,
    )
    auth = HTTPBasicAuth(
        credentials.client_id,
        credentials.client_secret)

    res = requests.post(uri, data=data, auth=auth)

    try:
        data = json.loads(res.content)
    except:
        print traceback.format_exc()

    if data.get('access_token', None):
        header, token, signature = data["access_token"].split('.')
        if data.get('id_token', None):
            iheader, itoken, isignature = data["id_token"].split('.')
        ctx = dict(
            signon=signon,
            request=request,
            data=data,
            header=_BD(header),
            token=_BD(token),
            id_token_header=_BD(iheader),
            id_token_token=_BD(itoken),
        )
    else:
        ctx = dict(
            signon=signon,
            request=request,
            data=data,
        )

    return TemplateResponse(
        request, 'rp/azure/res_code.html', ctx)
