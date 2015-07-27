import models
from django.core.urlresolvers import reverse
from connect.messages.discovery import ProviderMeta
from connect.api.token import TokenResource
from connect.api.userinfo import UserInfoResource
from connect.api.pubkey import AuthorityKeyResource
from connect.api.reg import RegResource

import urlparse

class Authority(object):

    @property
    def openid_configuration(self):
        meta = self.auth_metadata_object
        meta.issuer = self.identifier
        if self.tenant:
            meta['tenant'] = self.tenant
        return meta

    def update_uris(self):
        meta = self.auth_metadata_object

        meta.issuer=self.identifier

        meta.authorization_endpoint=self.default_authorization_endpoint()
        meta.token_endpoint=self.default_token_endpoint()
        meta.userinfo_endpoint=self.default_userinfo_endpoint()
        meta.registration_endpoint=self.default_registration_endpoint()

        meta.jwks_uri=self.default_jwks_uri()
        meta.tos_uri=self.default_tos_uri()
        meta.policy_uri=self.default_policy_uri()

        self.auth_metadata_object = meta
        self.save()

    def default_authorization_endpoint(self):
        return urlparse.urljoin(
            self.identifier,
            reverse('az_req', kwargs=dict(tenant=self.tenant)))

    def default_token_endpoint(self):
        return TokenResource.url(
            self.identifier, tenant=self.tenant)

    def default_userinfo_endpoint(self):
        return UserInfoResource.url(
            self.identifier, tenant=self.tenant)

    def default_registration_endpoint(self):
        return RegResource.url(
            self.identifier, tenant=self.tenant)

    def default_jwks_uri(self, jkuid=None):
        return AuthorityKeyResource.url(
            self.identifier, tenant=self.tenant, id=jkuid)

    def default_tos_uri(self, jkuid=None):
        return urlparse.urljoin(
            self.identifier,
            reverse('az_tos', kwargs=dict(tenant=self.tenant)))

    def default_policy_uri(self, jkuid=None):
        return urlparse.urljoin(
            self.identifier,
            reverse('az_policy', kwargs=dict(tenant=self.tenant)))
