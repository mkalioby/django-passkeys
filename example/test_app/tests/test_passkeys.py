from django.test import RequestFactory, TransactionTestCase, Client, override_settings

class test_passkeys(TransactionTestCase):
    def setUp(self) -> None:
        from django.contrib.auth import get_user_model

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test", password="test")
        self.client = Client()
        session = self.client.session
        self.factory = RequestFactory()

    def test_request_none_with_credentials_falls_through(self):
        """request=None with valid credentials delegates to ModelBackend regardless of settings."""
        from django.contrib.auth import authenticate
        user = authenticate(request=None, username="test", password="test")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test")

    def test_raiseException(self):
        """request=None with no credentials raises by default."""
        from django.contrib.auth import authenticate
        with self.assertRaises(Exception) as ctx:
            authenticate(request=None, username="", password="")
        self.assertEqual(str(ctx.exception), "request is required for passkeys.backend.PasskeyModelBackend")

    @override_settings(PASSKEYS_ALLOW_EMPTY_REQUEST=True)
    def test_request_none_returns_none_when_setting_enabled(self):
        """request=None returns None instead of raising when PASSKEYS_ALLOW_EMPTY_RESPONSE=True."""
        from django.contrib.auth import authenticate
        user = authenticate(request=None, username="", password="")
        self.assertIsNone(user)

    def test_not_add_passkeys_field(self):
        """Missing 'passkeys' POST field raises by default."""
        request = self.factory.post("/auth/login/", {"username": "", "password": ""})
        from django.contrib.auth import authenticate
        with self.assertRaises(Exception) as ctx:
            authenticate(request=request, username="", password="")
        self.assertEqual(str(ctx.exception), "Can't find 'passkeys' key in request.POST, did you add the hidden input?")

    @override_settings(PASSKEYS_ALLOW_NO_PASSKEY_FIELD=True)
    def test_not_add_passkeys_field_returns_none_when_setting_enabled(self):
        """Missing 'passkeys' POST field returns None when PASSKEYS_ALLOW_NO_PASSKEY_FIELD=True."""
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
