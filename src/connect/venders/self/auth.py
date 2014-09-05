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
from connect.messages.id_token import IdToken
from settings import create_authority, create_relyingparty 

from jose.base import JoseException
import traceback

SCOPES = ["profile", "email", ]
PROMPT = ["none", "consent", "select_account",]


def resolve_token(request, signon, vender):
    ''' resolve ID Token from SIOP AuthRes
    '''

    try:
        id_token = signon.get_id_token()
    except JoseException, ex:
        id_token = None

    if id_token is None  or not id_token.verified:
        #: TODO: raise Exception for each error.
        signon.subject = id_token and id_token.sub or None
        signon.save()
        raise Exception("invalid id_token")

    signon.subject = id_token.sub 
    signon.verified = id_token.is_available(signon.party.identifier)
    signon.save()
    if not signon.verified:
        raise Exception("invalid id_token")

    conf = signon.party.authority.auth_metadata_object
    access_token = signon.access_token 
    userinfo = None
    if conf and conf.userinfo_endpoint and access_token:
        headers = {
            "Authorization": "Bearer %s" % access_token, 
            "content-type": "application/json",
        }
        res = requests.get(conf.userinfo_endpoint, headers=headers)
        if res.status_code == 200:
            signon.userinfo = res.content    
            signon.save()

    return id_token


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

        signon = SignOn.create(
            request.user, rp, authreq, request.session.session_key )
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

    if not authres.id_token:
        raise Exception("No ID Token")

    signon = None
    errors = None
    try:
        signon = SignOn.objects.get(state=authres.state)

        # Save AuthRes
        signon.response_object = authres

        # Save Id Token
        id_token_string = signon.get_id_token_string() 
        if id_token_string:
            id_token = IdToken.parse_siop_token(id_token_string)
            signon.verified = id_token.verified
            signon.id_token_object = id_token
            signon.subject = id_token.sub 

        signon.save()

        if authres.error:
            raise Exception("authres error")

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
