# -*- coding: utf-8 -*-
'''
Windows Azure...
'''
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django import forms

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
from connect.messages.reg import ClientReg

from jose.base import JoseException
import traceback

import requests


class RelyingPartyForm(BaseRelyingPartyForm):
    client_id = forms.CharField(required=True) 
    client_secret = forms.CharField(required=True) 

    def __init__(self, data=None, instance=None, *args, **kwargs):
        if instance and not data:
            credentials = instance.reg_object
            self.base_fields['client_id'].initial = credentials.client_id
            self.base_fields['client_secret'].initial = credentials.client_secret
        
        super(RelyingPartyForm, self).__init__(
            data=data, instance=instance, *args, **kwargs)

    class Meta:
        model = RelyingParty
        exclude = ['authority', 'reg', 'auth_metadata', 'auth_settings',]
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
        request, 'venders/azure/settings_detail.html', ctx)


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
            raise Exception('Authority MUST be createed first with Azure Tenant Name')
        
        kwargs = dict(vender=vender, command="edit",)
        return HttpResponseRedirect(
            reverse('rp_settings', kwargs=kwargs))

    ctx = dict(
        request=request,
        parties=parties,
        vender=vender,
    )
    return TemplateResponse(
        request, 'venders/azure/settings_items.html', ctx)


@staff_member_required
def edit(request, vender, id, command):
    
    vender_name  = "connect.venders.%s" % vender
    instance= id and RelyingParty.objects.get(id=id)
    if request.method == "POST": 
        form = RelyingPartyForm(
            data=request.POST, instance=instance)
        if form.is_valid():
            form.instance.authority = Authority.objects.filter(vender=vender_name)[0]
            reg = ClientReg(
                client_id=form.cleaned_data['client_id'], 
                client_secret=form.cleaned_data['client_secret'], 
            )
            form.instance.reg_object = reg
            form.save() 
            return HttpResponseRedirect( 
                reverse('rp_settings', 
                       kwargs=dict(
                        vender=vender, id=form.instance.id,
                       ))
            )
        try:
            reg = form.instance.reg_object
        except Exception, ex:
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
        request, 'venders/azure/settings_edit.html', ctx)


def create_authority(tenant, *args, **kwargs):
    if not tenant:
        raise Exception("Tenant name is required for Azure Authroity")

    conf_uri = 'https://login.windows.net/%s/.well-known/openid-configuration' % tenant
    res = requests.get(conf_uri, headers={'content-type': 'application/json'}) 

    if res.status_code != 200:
        raise Exception("Failed to get OpenID Configuration")

    meta = ProviderMeta.from_json(res.content)
    authority, created = Authority.objects.get_or_create(
        identifier=meta.issuer,
        vender=__package__,
        tenant=tenant,
    )
    if created:
        authority.short_name = "Azure"
        authority.save()
    

    authority.auth_metadata_object = meta
    authority.save()

    authority.update_key()
    return authority
