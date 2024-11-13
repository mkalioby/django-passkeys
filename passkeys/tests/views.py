from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from passkeys.models import UserPasskey


class ViewsTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.user_model = get_user_model()

        self.user_a = self.user_model.objects.create_user(username="a", password="a")
        self.user_b = self.user_model.objects.create_user(username="b", password="b")

        UserPasskey.objects.create(user=self.user_a, name='UserPasskey A', credential_id='userpasskey-a', enabled=True)
        UserPasskey.objects.create(user=self.user_b, name='UserPasskey B', credential_id='userpasskey-b', enabled=True)

    def test_index(self):
        self.client.logout()

        # anonymous access
        response = self.client.post(reverse('passkeys:home'))
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username="a", password="a")

        # retrieve key list, check if correct keys are listed
        response = self.client.post(reverse('passkeys:home'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'UserPasskey A')
        self.assertNotContains(response, 'UserPasskey B')

    def test_key_toggle(self):
        self.client.logout()

        key = UserPasskey.objects.filter(user=self.user_a).latest('pk')

        # no anonymous access
        response = self.client.post(reverse('passkeys:toggle'), {"id": key.id})
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username="a", password="a")

        # enable key
        response = self.client.post(reverse('passkeys:toggle'), {"id": key.id})
        self.assertEqual(response.status_code, 200)
        key.refresh_from_db()
        self.assertFalse(key.enabled)

        # disable key
        response = self.client.post(reverse('passkeys:toggle'), {"id": key.id})
        self.assertEqual(response.status_code, 200)
        key.refresh_from_db()
        self.assertTrue(UserPasskey.objects.get(id=key.id).enabled)

        # ownership error
        key = UserPasskey.objects.filter(user=self.user_b).latest('pk')
        response = self.client.post(reverse('passkeys:toggle'), {"id": key.id})
        self.assertEqual(response.status_code, 403)
        key.refresh_from_db()
        self.assertTrue(UserPasskey.objects.get(id=key.id).enabled)

        # invalid key id
        response = self.client.post(reverse('passkeys:toggle'), {"id": 9999999})
        self.assertEqual(response.status_code, 403)
        key.refresh_from_db()
        self.assertTrue(UserPasskey.objects.get(id=key.id).enabled)

        response = self.client.post(reverse('passkeys:toggle'), {})
        self.assertEqual(response.status_code, 403)
    def test_key_delete(self):
        self.client.logout()
        key = UserPasskey.objects.filter(user=self.user_a).latest('pk')

        # no anonymous access
        response = self.client.post(reverse('passkeys:delKey'), {"id": key.id})
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username="a", password="a")

        # successful delete
        self.client.post(reverse('passkeys:delKey'), {"id": key.id})
        self.assertEqual(UserPasskey.objects.filter(id=key.id).count(), 0)

        # ownership error
        key = UserPasskey.objects.filter(user=self.user_b).latest('pk')
        response = self.client.post(reverse('passkeys:delKey'), {"id": key.id})
        self.assertEqual(response.status_code, 403)

        # invalid key id
        response = self.client.post(reverse('passkeys:delKey'), {"id": 9999999})
        self.assertEqual(response.status_code, 403)

        #Missing Parameter
        response = self.client.post(reverse('passkeys:delKey'), {})
        self.assertEqual(response.status_code, 403)
