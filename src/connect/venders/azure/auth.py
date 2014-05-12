# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn
)
from connect.rp.views import save_signon, bind

from connect.messages.auth import AuthReq, AuthResCode


def req_any(request):
    form = AuthReqForm(
        vender=__package__,
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

        signon = SignOn.create(request.user, rp, authreq)
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
        'venders/azure/req_any.html',
        dict(request=request, form=form))


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

    save_signon(request, signon)

    credentials = signon.party.credentials

    uri = signon.party.authority.openid_configuration.token_endpoint
    ruri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
            vender='azure', action='res', mode='code',
        ))
    )
    data = dict(
        grant_type="authorization_code",
        code=request.GET.get('code'),
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        resource="https://graph.windows.net",
        redirect_uri=ruri,
    )

    auth = HTTPBasicAuth(
        credentials.client_id,
        credentials.client_secret)

    res = requests.post(uri, data=data, auth=auth)
    signon.tokens = res.content
    id_token = signon.id_token
    if id_token:        #: verfied
        signon.subject = id_token.sub
        signon.verified = True
        signon.save()

        return bind(request, signon)

    signon.save()

    ctx = {}    #: TODO:ERROR
    return TemplateResponse(
        request, 'venders/azure/res_code.html', ctx)
