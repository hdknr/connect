# -*- coding: utf-8 -*
from django.template.response import TemplateResponse
from django.http.response import HttpResponseRedirect, Http404
from django.contrib.auth import login
from django.utils.importlib import import_module
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate

from forms import AuthReqForm, SignUpForm, SelectForm
from connect.rp.models import SignOn, Identity, Authority, RelyingParty
from connect.messages.id_token import IdToken
from jose.base import JoseException
from django.conf import settings as app_settings

import requests

def save_signon(request, signon):
    request.session['rp_signon'] = signon.id


def load_signon(request):
    return SignOn.objects.get(id=request.session['rp_signon'])


def auth_login(request, user):
    user = authenticate(user=user)
    login(request, user)


#def su(request, redir):
#    signon = request.session.get('rp_signon', None)
#    logout(request)
#
#    engine = import_module(settings.SESSION_ENGINE)
#    request.session = engine.SessionStore()
#    save_signon(request, signon)
#    request.session.save()
#
#    return HttpResponseRedirect(redir)


def request_token(request, signon, vender):
    '''
    '''

    credentials = signon.party.reg_object

    uri = signon.party.authority.auth_metadata_object.token_endpoint
    ruri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
            vender=vender, action='res', mode='code',
        ))
    )
    data = dict(
        grant_type="authorization_code",
        code=request.GET.get('code'),
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        redirect_uri=ruri,
    )

    auth = requests.auth.HTTPBasicAuth(
        credentials.client_id,
        credentials.client_secret)

    res = requests.post(uri, data=data, auth=auth)
    signon.tokens = res.content
    signon.save()

    try:
        id_token = signon.get_id_token()
    except JoseException, ex:
        id_token = None

    if id_token is None  or not id_token.verified:
        signon.subject = id_token and id_token.sub or None
        signon.save()
        raise Exception("invalid id_token")

    #: TODO other id token values
    signon.subject = id_token.sub 
    signon.verified = True
    signon.save()

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


def default(request):
    return TemplateResponse(
        request,
        'venders/core/req_any.html',
        dict(request=request,
             form=AuthReqForm()))


def auth(request, vender, action, mode, *args, **kwargs):
    mod = import_module(
        "connect.venders.%s.auth" % (vender.split('.')[-1] or "core"))
    func = "%s_%s" % (action, mode or "any")
    return getattr(mod, func)(request, vender, action, mode, *args, **kwargs)


def settings(request, 
             vender, id, command,  
             *args, **kwargs):
    mod = import_module(
        "connect.venders.%s.settings" % (vender or "core"))
    func = "%s" % ( command or "default")
    return getattr(mod, func)(request, vender, id, command, *args, **kwargs)


def preference(request, 
             vender, id, command,  
             *args, **kwargs):
    mod = import_module(
        "connect.venders.%s.preference" % (vender or "core"))
    func = "%s" % ( command or "default")
    return getattr(mod, func)(request, vender, id, command, *args, **kwargs)


def bind(request, signon=None):
    signon = signon or load_signon(request)

    if request.user.is_authenticated():
        identity, created = signon.party.rp_identity_related.get_or_create(
            authority=signon.authority,
            subject=signon.subject,
            user=request.user)
        print ">>>> current", signon.id_token
        identity.id_token_object  = signon.id_token_object
        identity.save()
        signon.user = request.user
        signon.save()

        return HttpResponseRedirect('/')       # TODO:

    identities = signon.identities
    if identities.count() == 1:
        identity = identities[0]
        auth_login(request, identity.user)
        identity.id_token = signon.id_token
        identity.save()
        print ">>>> comeback ", signon.id_token, identity.id_token,
        print request.user, request.user.is_authenticated()
        
        
        signon.user = request.user
        signon.save()
        return HttpResponseRedirect('/')       # TODO:

    save_signon(request, signon)    # Save SingOn object in session

    #: TODO: Appcaition MUST be able to specify forms.
    if identities.count() == 0:
        print ">>> sign up"
        form = SignUpForm(signon=signon)
    else:
        print ">>> selection (NO!)"
        form = SelectForm(signon=signon)

    return TemplateResponse(
        request,
        form.template_name,
        dict(request=request, form=form))


def select(request):
    if request.method == "GET":
        return Http404

    signon = load_signon(request)

    form = SelectForm(signon=signon, data=request.POST)
    if form.is_valid():
        auth_login(request, form.cleaned_data['identity'].user)
        signon.user = request.user
        signon.save()
        return HttpResponseRedirect('/')       # TODO:

    return TemplateResponse(
        request,
        form.template_name,
        dict(request=request, form=form))


def signup(request):
    if request.method == "GET":
        return Http404

    signon = load_signon(request)

    form = SignUpForm(signon, data=request.POST or None)
    
    if form.is_valid():
        auth_login(request, user=form.create_user())
        signon.user = request.user
        signon.save()

        signon.party.rp_identity_related.get_or_create(
            authority=signon.authority,
            subject=signon.subject,
            user=request.user)

        return HttpResponseRedirect('/')       # TODO:

    return TemplateResponse(
        request,
        form.template_name,
        dict(request=request, form=form))


def connect(request):
    form = AuthReqForm(vender=None, data=request.POST or None) 
    if request.method == "POST" and form.is_valid(): 
        rp = form.cleaned_data['rp']
        return auth(request, 
            rp.authority.vender, "req", None)

    return TemplateResponse(
        request,
        "rp/connect.html",
        dict(request=request, form=form))


@login_required
def conf_default(request):
    return TemplateResponse(
        request,
        'rp/conf_default.html',
        dict(request=request))


@login_required
def identity_list(request):
    identity_list = Identity.objects.filter(user=request.user)
    return TemplateResponse(
        request,
        'rp/identity_list.html',
        dict(request=request, identity_list=identity_list))


@login_required
def identity_detail(request, id):
    identity = Identity.objects.get(id=id)
    signon_list = SignOn.objects.filter(
        party=identity.party,
        subject=identity.subject
    )

    return TemplateResponse(
        request,
        'rp/identity_detail.html',
        dict(request=request, 
             identity=identity,
             signon_list=signon_list,
            )   
    )


@login_required
def signon_detail(request, id):
    signon = SignOn.objects.get(id=id)
    if signon.subject:
        identity = Identity.objects.get(user=request.user, subject=signon.subject)
    else:
        return Http404
    id_token = signon.id_token_object

    return TemplateResponse(
        request,
        'rp/signon_detail.html',
        dict(request=request, 
             identity=identity,
             signon=signon,
             id_token=id_token,
            ))


@login_required
def authority_detail(request, id):
    authority = Authority.objects.get(id=id)

    return TemplateResponse(
        request,
        'rp/authority_detail.html',
        dict(request=request, 
             identity=identity,
             signon=signon,
             id_token=id_token,
            ))


@login_required
def userinfo(request, id):
    signon = SignOn.objects.get(id=id)
    if signon.subject:
        identity = Identity.objects.get(user=request.user, subject=signon.subject)
    else:
        identity = None
    
    id_token = signon.id_token
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
            identity.userinfo = res.content    
            identity.save()

        userinfo = res.content
    else:   
        identity.userinfo = id_token.to_json(indent=2)
        identity.save()
    

    return TemplateResponse(
        request,
        'rp/signon_detail.html',
        dict(request=request, 
             identity=identity,
             signon=signon,
             id_token=id_token,
             userinfo=userinfo,
            ))

