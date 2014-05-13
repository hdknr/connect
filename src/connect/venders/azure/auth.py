# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn
)
from connect.rp.views import save_signon, bind, request_token

from connect.messages.auth import AuthReq, AuthRes
import traceback


def req_any(request, vender, action, mode, *args, **kwargs):
    form = AuthReqForm(
        vender=__package__,
        data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        rp = form.cleaned_data['rp']
        conf = rp.authority.auth_metadata_object

        ruri = request.build_absolute_uri(
            reverse('rp_auth', kwargs=dict(
                vender='azure', action='res', mode='code',
            ))
        )
        authreq = AuthReq(
            response_type="code",
            client_id=rp.identifier,
            redirect_uri=ruri,
            scope="openid profile email",
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
        request, 'venders/azure/res_error.html', ctx)

