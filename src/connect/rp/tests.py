from django.test import TestCase


class UnitRpAuthority(TestCase):

    def test_selfissued(self):
        from connect.rp.models import Authority
        from connect.messages.discovery import ProviderMeta
        a = Authority.get_selfissued()
        self.assertEqual(a.identifier, ProviderMeta.selfissued_issuer)


class UnitRpSignOn(TestCase):
    def test_create(self):
        from connect.rp.models import RelyingParty
        r = RelyingParty.get_selfissued('http://hoge.com/')

        from connect.messages.auth import AuthReq
        authreq = AuthReq(
            redirect_uri=r.identifier
        )

        from connect.rp.models import SignOn
        s = SignOn.create(r, authreq)
        print s.nonce, s.state, s.request
        print authreq.to_qs()
