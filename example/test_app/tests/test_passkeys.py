from django.core.exceptions import SuspiciousOperation
from django.test import RequestFactory, TransactionTestCase, Client


class test_passkeys(TransactionTestCase):
    def setUp(self) -> None:
        from django.contrib.auth import get_user_model

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test", password="test")
        self.client = Client()
        self.factory = RequestFactory()

    def test_raiseException(self):
        from django.contrib.auth import authenticate

        with self.assertRaises(SuspiciousOperation) as ctx:
            authenticate(request=None, username="test", password="test")
        self.assertEqual(str(ctx.exception), "request is required for passkeys.backend.PasskeyModelBackend")

    def test_not_add_passkeys_field(self):
        request = self.factory.post("/auth/login", {"username": "", "password": ""})
        from django.contrib.auth import authenticate

        with self.assertRaises(SuspiciousOperation) as ctx:
            authenticate(request=request, username="", password="")
        self.assertEqual(str(ctx.exception), "Can't find 'passkeys' key in request.POST, did you add the hidden input?")

    def test_username_password_failed_login(self):
        self.client.post("/auth/login", {"username": "test", "password": "test123", 'passkeys': ''})
        self.assertFalse(self.client.session.get('_auth_user_id', False))

    def test_username_password_login(self):
        self.client.post("/auth/login", {"username": "test", "password": "test", 'passkeys': ''})
        self.assertTrue(self.client.session.get('_auth_user_id', False))
        self.assertFalse(self.client.session.get('passkey', {}).get('passkey', False))

    def test_no_data(self):
        self.client.post("/auth/login", {"username": "", "password": "", 'passkeys': ''})
        self.assertFalse(self.client.session.get('_auth_user_id', False))
