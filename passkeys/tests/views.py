from django.test import TransactionTestCase
from django.urls import reverse

from passkeys.models import UserPasskey


class KeyManagementTestcase(TransactionTestCase):

    def setUp(self) -> None:
        from django.contrib.auth import get_user_model
        self.user_model = get_user_model()

        user_a = self.user_model.objects.create_user(username="a", password="a")
        user_b = self.user_model.objects.create_user(username="b", password="b")

        UserPasskey.objects.create(pk=1, user=user_a, credential_id='A')
        UserPasskey.objects.create(pk=2, user=user_b, credential_id='B')

        self.client.login(username="a", password="a")

    def test_toggle(self):
        # wrong http method
        response = self.client.get(reverse('passkeys:toggle', args=[1]))
        self.assertEqual(response.status_code, 405)

        # disable key
        response = self.client.post(reverse('passkeys:toggle', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPasskey.objects.get(pk=1).enabled, False)

        # enable key
        response = self.client.post(reverse('passkeys:toggle', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPasskey.objects.get(pk=1).enabled, True)

        # key belongs to another user
        response = self.client.post(reverse('passkeys:toggle', args=[2]))
        self.assertEqual(response.status_code, 400)

        # key does not exist
        response = self.client.post(reverse('passkeys:toggle', args=[3]))
        self.assertEqual(response.status_code, 400)

    def test_delete(self):
        # wrong http method
        response = self.client.get(reverse('passkeys:delete', args=[1]))
        self.assertEqual(response.status_code, 405)

        # check if key exists
        self.assertEqual(UserPasskey.objects.filter(pk=1).exists(), True)

        # delete key
        response = self.client.delete(reverse('passkeys:delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserPasskey.objects.filter(pk=1).exists(), False)

        # key belongs to another user
        self.assertEqual(UserPasskey.objects.filter(pk=2).exists(), True)
        response = self.client.delete(reverse('passkeys:delete', args=[2]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(UserPasskey.objects.filter(pk=2).exists(), True)

        # key does not exist
        self.assertEqual(UserPasskey.objects.filter(pk=3).exists(), False)
        response = self.client.delete(reverse('passkeys:delete', args=[3]))
        self.assertEqual(response.status_code, 400)
