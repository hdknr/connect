from django.test import TestCase


class UnitRpAuthority(TestCase):

    def test_selfissued(self):
        from connect.rp.models import Authority
        from connect.messages.discovery import ProviderMeta
        a = Authority.get_selfissued()
        self.assertEqual(a.identifier, ProviderMeta.selfissued_issuer)


class UnitRpKey(TestCase):

    def test_create(self):
        from connect.rp.models import RelyingParty
        r = RelyingParty.get_selfissued('http://key.com/')
        self.assertEqual(r.keys.count(), 0)
        self.assertEqual(r.authority.keys.count(), 0)

        from jose.jwk import Jwk, JwkSet
        from jose.jwa import keys

        jwkset = JwkSet()
        jwkset.keys.append(Jwk(kid='kidRsa', kty=keys.KeyTypeEnum.RSA))
        jwkset.keys.append(Jwk(kid='kidEc', kty=keys.KeyTypeEnum.EC))
        jwkset.keys.append(Jwk(kid='kidOct', kty=keys.KeyTypeEnum.OCT))
        jwkset.save(r)

        self.assertEqual(r.keys.count(), 1)
        self.assertEqual(r.authority.keys.count(), 0)

        jwkset.save(r.authority)
        self.assertEqual(r.keys.count(), 1)
        self.assertEqual(r.authority.keys.count(), 1)


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
