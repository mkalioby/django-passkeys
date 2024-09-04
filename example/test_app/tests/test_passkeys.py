from django.test import RequestFactory,TransactionTestCase, Client

class test_passkeys(TransactionTestCase):
    def setUp(self) -> None:
        from django.contrib.auth import get_user_model
        if not getattr(self, "assertEquals", None):
            self.assertEquals = self.assertEqual

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test",password="test")
        self.client = Client()
        self.factory = RequestFactory()

    def test_raiseException(self):
        from django.contrib.auth import authenticate
        try:
             authenticate(request=None,username="test",password="test")
             self.assertFalse(True)
        except Exception as e:
            self.assertEquals(str(e),"request is required for passkeys.backend.PasskeyModelBackend")

    def test_not_add_passkeys_field(self):
        request = self.factory.post("/auth/login",{"username":"","password":""})
        from django.contrib.auth import authenticate
        try:
            user = authenticate(request=request,username="",password="")
            self.assertFalse(True)
        except Exception as e:
            self.assertEquals(str(e),"Can't find 'passkeys' key in request.POST, did you add the hidden input?")

    def test_username_password_failed_login(self):
        self.client.post("/auth/login",{"username":"test","password":"test123",'passkeys':''})
        self.assertFalse(self.client.session.get('_auth_user_id',False))

    def test_username_password_login(self):
        self.client.post("/auth/login",{"username":"test","password":"test",'passkeys':''})
        self.assertTrue(self.client.session.get('_auth_user_id',False))
        self.assertFalse(self.client.session.get('passkey', {}).get('passkey', False))

    def test_no_data(self):
        self.client.post("/auth/login",{"username":"","password":"",'passkeys':''})
        self.assertFalse(self.client.session.get('_auth_user_id',False))
