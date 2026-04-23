from django.test import RequestFactory,TransactionTestCase, Client

class test_passkeys(TransactionTestCase):
    def setUp(self) -> None:
        from django.contrib.auth import get_user_model

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test",password="test")
        self.client = Client()
        session = self.client.session
        self.factory = RequestFactory()

    def test_request_none_with_credentials_falls_through(self):
        """When request=None, username/password auth should still work via ModelBackend."""
        from django.contrib.auth import authenticate
        user = authenticate(request=None, username="test", password="test")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test")

    def test_request_none_without_credentials_returns_none(self):
        """When request=None and no credentials, backend should return None."""
        from django.contrib.auth import authenticate
        user = authenticate(request=None, username="", password="")
        self.assertIsNone(user)

    def test_not_add_passkeys_field(self):
        """Missing 'passkeys' POST field should return None, not raise."""
        request = self.factory.post("/auth/login/", {"username": "", "password": ""})
        from django.contrib.auth import authenticate
        user = authenticate(request=request, username="", password="")
        self.assertIsNone(user)

    def test_username_password_failed_login(self):
        self.client.post("/auth/login/",{"username":"test","password":"test123",'passkeys':''})
        self.assertFalse(self.client.session.get('_auth_user_id',False))

    def test_username_password_login(self):
        self.client.post("/auth/login/",{"username":"test","password":"test",'passkeys':''})
        self.assertTrue(self.client.session.get('_auth_user_id',False))
        self.assertFalse(self.client.session.get('passkey', {}).get('passkey', False))

    def test_no_data(self):
        self.client.post("/auth/login/",{"username":"","password":"",'passkeys':''})
        self.assertFalse(self.client.session.get('_auth_user_id',False))
