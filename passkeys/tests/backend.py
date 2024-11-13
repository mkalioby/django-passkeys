from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from passkeys.backend import PasskeyModelBackend


class PasskeyModelBackendTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test", password="test")

    def test_username_password_failed(self):
        backend = PasskeyModelBackend()
        user = backend.authenticate(None, 'test', 'test123')
        self.assertEqual(user, None)

    def test_username_password_success(self):
        backend = PasskeyModelBackend()
        user = backend.authenticate(None, 'test', 'test')
        self.assertNotEqual(user, None)

    def test_username_password_success(self):
        backend = PasskeyModelBackend()
        user = backend.authenticate(None, 'test', 'test')
        self.assertNotEqual(user, None)
