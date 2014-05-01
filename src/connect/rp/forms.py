# -*- coding: utf-8 -*-

from django import forms
from connect.rp.models import RelyingParty
#from django.utils.translation import ugettext_lazy as _


class AuthReqForm(forms.Form):
    identifier = forms.CharField(required=False)
    rp = forms.ModelChoiceField(required=False, queryset=None)

    def __init__(self, vender='connect.rp.core', *args, **kwargs):
        qset = RelyingParty.objects.filter(authority__vender=vender)
        self.base_fields["rp"].queryset = qset
        super(AuthReqForm, self).__init__(*args, **kwargs)
