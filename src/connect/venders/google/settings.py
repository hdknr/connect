# -*- coding: utf-8 -*-
'''
Google "OAuth 2.0 for Login(OpenID Connect)"
https://developers.google.com/accounts/docs/OAuth2Login
'''
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from connect.rp.forms import AuthReqForm
from connect.rp.models import (
    SignOn,
    RelyingParty,
    Authority,
)
from connect.rp.views import save_signon, bind
from connect.rp.forms import RelyingPartyForm as BaseRelyingPartyForm

from connect.messages.auth import AuthReq, AuthResCode, AuthRes
from connect.messages.discovery import ProviderMeta

from jose.base import JoseException
import traceback

import requests


class RelyingPartyForm(BaseRelyingPartyForm):
    pass


@staff_member_required
def default(request, vender, id, command):
    if id is None:
        return items(request, vender, id, 'items')

    ctx = dict(
        request=request,
        party=RelyingParty.objects.get(id=id),
        vender=vender,
        
    )
    return TemplateResponse(
        request, 'venders/google/settings_detail.html', ctx)


@staff_member_required
def items(request, vender, id, command):
    ''' 
    '''
    #:TODO: if no RelyingParty, create default and edit it.

    vender_name  = "connect.venders.%s" % vender
    parties = RelyingParty.objects.filter(
        authority__vender=vender_name
    )
    if parties.count() < 1: 
        if not Authority.objects.filter(vender=vender_name).exists():
            #: TODO: Crete Vender
            authority = create_authority()
        
        kwargs = dict(vender=vender, command="edit",)
        return HttpResponseRedirect(
            reverse('rp_settings', kwargs=kwargs))

    ctx = dict(
        request=request,
        parties=parties,
        vender=vender,
    )
    return TemplateResponse(
        request, 'venders/google/settings_items.html', ctx)


@staff_member_required
def edit(request, vender, id, command):
    
    vender_name  = "connect.venders.%s" % vender
    instance= id and RelyingParty.objects.get(id=id)
    if request.method == "POST": 
        form = RelyingPartyForm(
            data=request.POST, instance=instance)
        if form.is_valid():
            form.instance.authority = Authority.objects.filter(vender=vender_name)[0]
            form.save() 
            return HttpResponseRedirect( 
                reverse('rp_settings', 
                       kwargs=dict(
                        vender=vernder, id=id 
                       ))
            )
        try:
            reg = form.instance.credentials
        except Exception, ex:
            print ex
            pass
    else:
        form = RelyingPartyForm(instance=instance)

    redirect_uri = request.build_absolute_uri(
        reverse('rp_auth', kwargs=dict(
        vender=vender, action='res', mode='code',
        ))
    )

    ctx = dict(
        request=request,
        form=form,
        redirect_uri=redirect_uri,
        vender=vender,
    )
    return TemplateResponse(
        request, 'venders/google/settings_edit.html', ctx)


def create_authority(tenant=None, *args, **kwargs):
    conf_uri = 'https://accounts.google.com/.well-known/openid-configuration'
    authority, created = Authority.objects.get_or_create(
        identifier='accounts.google.com', 
        vender=__package__,
    )
    if tenant:
        authority.tenant = tenant

    if created:
        authority.short_name = "Google"
        authority.save()
    
    res = requests.get(conf_uri, headers={'content-type': 'application/json'}) 
    if res.status_code != 200:
        raise Exception("Failed to get OpenID Configuration")

    authority.auth_metadata_object = ProviderMeta.from_json(res.content)
    authority.save()

    authority.update_key()
    return authority
