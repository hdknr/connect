import models
from connect.messages.discovery import ProviderMeta

class Authority(object):

    @property
    def openid_configuration(self):
        meta = self.auth_metadata_object
        meta.issuer = self.identifier
        if self.tenant:
            meta['tenant'] = self.tenant
        return meta

    def create_default_authmetadata(self):
        self.auth_metadata_object = ProviderMeta(
            issuer=self.identifier,
        )
        self.save()

