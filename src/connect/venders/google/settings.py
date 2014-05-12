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

from jose.base import JoseException
import traceback



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
            pass

    ctx = dict(
        request=request,
        parties=parties,
        vender=vender,
    )
    return TemplateResponse(
        request, 'venders/google/settings_items.html', ctx)


@staff_member_required
def edit(request, vender, id, command):
    
    instance=RelyingParty.objects.get(id=id)
    if request.method == "post": 
        form = RelyingPartyForm(
            data=request.POST, instance=instance)
        if form.is_valid:
            form.save() 
            return HttpResponseRedirect( 
                revers('rp_settings', 
                       kwargs=dict(
                        vender=vernder, id=id 
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
        request, 'venders/google/settings_edit.html', ctx)
