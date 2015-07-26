from django.test import TestCase


class UnitAzAuthority(TestCase):

    def test_get(self):
        from connect.az.models import Authority
        a, c = Authority.objects.get_or_create(
            identifier="http://hoge.com/hoge",
            tenant="hoge")
        self.assertTrue(c)
        self.assertEqual(a.auth_metadata, '{}')

    def test_selfissued(self):
        from connect.az.models import Authority
        from connect.messages.discovery import ProviderMeta
        a = Authority.get_selfissued()
        self.assertEqual(a.identifier, ProviderMeta.selfissued_issuer)
