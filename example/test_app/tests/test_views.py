from django.test import TransactionTestCase, Client
from django.urls import reverse

from passkeys.models import UserPasskey
from .test_fido import test_fido

class test_views(TransactionTestCase):

    def setUp(self) -> None:
        from django.contrib.auth import get_user_model
        if not getattr(self, "assertEquals", None):
            self.assertEquals = self.assertEqual

        self.user_model = get_user_model()
        #self.user = self.user_model.objects.create_user(username="test", password="test")
        self.client = Client()
        #self.client.post("/auth/login", {"username": "test", "password": "test", 'passkeys': ''})
        test = test_fido()
        test.setUp()
        self.authenticator = test.test_key_reg()
        self.client.post("/auth/login", {"username": "test", "password": "test", 'passkeys': ''})
        self.user = self.user_model.objects.get(username="test")

    def test_disabling_key(self):
        key =UserPasskey.objects.filter(user=self.user).latest('id')
        self.client.get(reverse('passkeys:toggle') + "?id=" + str(key.id))
        self.assertFalse(UserPasskey.objects.get(id=key.id).enabled)

        self.client.get(reverse('passkeys:toggle') + "?id=" + str(key.id))
        self.assertTrue(UserPasskey.objects.get(id=key.id).enabled)

    def test_deleting_key(self):
        key = UserPasskey.objects.filter(user=self.user).latest('id')
        self.client.get(reverse('passkeys:delKey') + "?id=" + str(key.id))
        self.assertEquals(UserPasskey.objects.filter(id=key.id).count(), 0)

    def test_wrong_ownership(self):
        test = test_fido()
        test.setUp()
        authenticator = test.test_key_reg()
        key = UserPasskey.objects.filter(user=self.user).latest('id')
        self.user = self.user_model.objects.create_user(username="test2", password="test2")
        self.client.post("/auth/login", {"username": "test2", "password": "test2", 'passkeys': ''})
        r = self.client.get(reverse('passkeys:delKey') + "?id="+str(key.id))
        self.assertEquals(r.status_code, 403)
        self.assertEquals(r.content,b"Error: You own this token so you can't delete it")
        r = self.client.get(reverse('passkeys:toggle') + "?id=" + str(key.id))
        self.assertEquals(r.status_code, 403)
        self.assertEquals(r.content, b"Error: You own this token so you can't toggle it")
