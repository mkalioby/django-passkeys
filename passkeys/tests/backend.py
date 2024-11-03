from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from passkeys.backend import PasskeyModelBackend


class PasskeyModelBackendTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test", password="test")
        self.backend = PasskeyModelBackend()

    def test_username_password_login(self):
        result = self.backend.authenticate(None, username="test", password="test")
        self.assertNotEqual(result, None)

    def test_username_password_failed_login(self):
        result = self.backend.authenticate(None, username="test", password="test1")
        self.assertEqual(result, None)

    def test_no_data(self):
        result = self.backend.authenticate(None, username="", password="")
        self.assertEqual(result, None)
