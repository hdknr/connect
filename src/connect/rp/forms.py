# -*- coding: utf-8 -*-

from django import forms
from connect.rp.models import RelyingParty
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model

from models import RelyingParty


class AuthReqForm(forms.Form):
    identifier = forms.CharField(
        required=False, label=_(u'OP Identifier'))
    rp = forms.ModelChoiceField(
        required=False, queryset=None, label=_(u'Relying Party'))

    def __init__(self, vender='connect.rp.core', *args, **kwargs):
        if vender:
            qset = RelyingParty.objects.filter(authority__vender=vender)
        else:
            qset = RelyingParty.objects.all()
            
        self.base_fields["rp"].queryset = qset
        super(AuthReqForm, self).__init__(*args, **kwargs)


class SignUpForm(forms.Form):
    url_name = 'rp_signup'
    template_name = 'rp/signup.html'
    signon = forms.IntegerField(widget=forms.HiddenInput, required=False,)

    username = forms.CharField(label=_(u'User Name'), required=True,)
    password = forms.CharField(label=_(u'Password'), required=True,
                               widget=forms.PasswordInput())
    email = forms.EmailField(required=True)

    def __init__(self, signon=None, *args, **kwargs):
        self.signon = signon
        if signon:
            self.base_fields["signon"].initial = signon.id

        super(SignUpForm, self).__init__(*args, **kwargs)

    def create_user(self):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password'])
        return user

    def url(self):
        return reverse(self.url_name)


class SelectForm(forms.Form):
    url_name = 'rp_select'
    template_name = 'rp/select.html'
    signon = forms.IntegerField(widget=forms.HiddenInput, required=False,)

    identity = forms.ModelChoiceField(required=True, queryset=None)

    def __init__(self, signon=None, *args, **kwargs):
        self.signon = signon
        if signon:
            self.base_fields["identity"].queryset = signon.identities
            self.base_fields["signon"].initial = signon.id

        super(SelectForm, self).__init__(*args, **kwargs)

    def url(self):
        return reverse(self.url_name)


class BindForm(forms.Form):
    url_name = 'rp_bind'
    template_name = 'rp/bind.html'
    signon = forms.IntegerField(widget=forms.HiddenInput, required=False,)

    def __init__(self, signon=None, *args, **kwargs):
        if signon:
            self.base_fields["signon"].initial = signon.id

        super(BindForm, self).__init__(*args, **kwargs)

    def url(self):
        return reverse(self.url_name)


class SignInForm(forms.Form):
    url_name = 'rp_signin'
    template_name = 'rp/signin.html'
    signon = forms.IntegerField(widget=forms.HiddenInput, required=False,)

    username = forms.CharField(label=_(u'User Name'), required=True,)
    password = forms.CharField(label=_(u'Password'), required=True,
                               widget=forms.PasswordInput())

    error_messages = {
        'invalid_login': _(u"Invalid Login"),
        'no_cookies': _(u"No Cookies"),
        'inactive': _(u"This account is inactive."),
    }

    def __init__(self, signon=None, request=None, *args, **kwargs):
        self.signon = signon
        if signon:
            self.base_fields["signon"].initial = signon.id

        self.request = request
        self.user_cache = None
        super(SignUpForm, self).__init__(*args, **kwargs)

        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(
            UserModel.USERNAME_FIELD)

        if not self.fields['username'].label:
            self.fields['username'].label = capfirst(
                self.username_field.verbose_name)

    def url(self):
        return reverse(self.url_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class RelyingPartyForm(forms.ModelForm):

    class Meta:
        model = RelyingParty
        exclude = ['keys', 'authority', ]
