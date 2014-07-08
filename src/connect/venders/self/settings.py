# -*- coding: utf-8 -*-
'''
Self Issued OP

https://openid.net/specs/openid-connect-core-1_0.html#SelfIssued
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
    class Meta:
        model = RelyingParty
        exclude = ['authority', 'auth_settings', 'auth_metadata',]
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
        request, 
        'venders/%s/settings_detail.html'  % vender, ctx)


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
        request, 
        'venders/%s/settings_items.html' % vender, ctx)


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
                        vender=vender, id=form.instance.id,
                       ))
            )
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
        request, 
        'venders/%s/settings_edit.html' % vender, ctx)


def create_authority(tenant=None, *args, **kwargs):

    authority, created = Authority.objects.get_or_create(
        identifier='https://self-issued.me',        # Connect 7.1
        vender=__package__,
    )
    if tenant:
        authority.tenant = tenant

    if created:
        authority.short_name = "SelfIssued"
        authority.save()
    
    meta = '''
    {
       "authorization_endpoint":
         "openid:",
       "issuer":
         "https://self-issued.me",
       "scopes_supported":
         ["openid", "profile", "email", "address", "phone"],
       "response_types_supported":
         ["id_token"],
       "subject_types_supported":
         ["pairwise"],
       "id_token_signing_alg_values_supported":
         ["RS256"],
       "request_object_signing_alg_values_supported":
         ["none", "RS256"]
    }'''

    authority.auth_metadata_object = ProviderMeta.from_json(meta)
    authority.save()

    #: Authoriy public key can not be resolved.
    return authority
