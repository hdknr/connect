# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.http.response import HttpResponseRedirect, Http404
from django.contrib.auth import login
from django.utils.importlib import import_module
from django.contrib.auth.decorators import login_required

from forms import AuthReqForm, SignUpForm, SelectForm
from connect.rp.models import SignOn, Identity, Authority
from connect.messages.id_token import IdToken


def save_signon(request, signon):
    request.session['rp_signon'] = signon.id


def load_signon(request):
    return SignOn.objects.get(id=request.session['rp_signon'])


def auth_login(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
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


def default(request):
    return TemplateResponse(
        request,
        'venders/core/req_any.html',
        dict(request=request,
             form=AuthReqForm()))


def auth(request, vender, action, mode, *args, **kwargs):
    mod = import_module(
        "connect.venders.%s.views" % (vender or "core"))
    func = "%s_%s" % (action, mode or "any")
    return getattr(mod, func)(request, *args, **kwargs)


def bind(request, signon=None):
    signon = signon or load_signon(request)

    if request.user.is_authenticated():
        signon.party.rp_identity_related.get_or_create(
            authority=signon.authority,
            subject=signon.subject,
            user=request.user)
        signon.user = request.user
        signon.save()

        return HttpResponseRedirect('/')       # TODO:

    identities = signon.identities
    if identities.count() == 1:
        auth_login(request, identities[0].user)
        signon.user = request.user
        signon.save()
        return HttpResponseRedirect('/')       # TODO:

    save_signon(request, signon)

    #: TODO: Appcaition MUST be able to specify forms.
    if identities.count() == 0:
        form = SignUpForm(signon=signon)
    else:
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

    form = SignUpForm(signon, data=request.POST)
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
    id_token = signon.id_token

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
