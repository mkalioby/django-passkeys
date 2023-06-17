import json

from django.test import RequestFactory,TransactionTestCase, Client
from django.urls import reverse

from test_app.soft_webauthn import SoftWebauthnDevice


class test_fido(TransactionTestCase):
    def setUp(self) -> None:
        from django.contrib.auth import get_user_model
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username="test",password="test")
        self.client = Client()
        self.client.post("/auth/login", {"username": "test", "password": "test", 'passkeys': ''})
        self.factory = RequestFactory()


    def test_key_reg(self):
        r = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        j['publicKey']['challenge'] = j['publicKey']['challenge'].encode("ascii")
        s = SoftWebauthnDevice()
        res = s.create(j, "https://" + j["publicKey"]["rp"]["id"])
        res["key_name"]="testKey"
        u = reverse('passkeys:reg_complete')
        r = self.client.post(u, data=json.dumps(res),headers={"USER_AGENT":""}, HTTP_USER_AGENT="", content_type="application/json")
        try:
            j = json.loads(r.content)
        except Exception:
            raise AssertionError("Failed to get the required JSON after reg_completed")
        self.assertTrue("status" in j)

        self.assertEquals(j["status"], "OK")
        return s


    def test_passkey_login(self):
        authenticator = self.test_key_reg()
        self.client.get('/auth/logout')
        r = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        j['publicKey']['challenge'] = j['publicKey']['challenge'].encode("ascii")

        res = authenticator.get(j, "https://" + j["publicKey"]["rpId"])
        u = reverse('login')
        self.client.post(u, {'passkeys': json.dumps(res), "username": "", "password": ""},headers={"USER_AGENT":""}, HTTP_USER_AGENT="")
        self.assertTrue(self.client.session.get('_auth_user_id',False))
        self.assertTrue(self.client.session.get("passkey",{}).get("passkey",False))
        self.assertEquals(self.client.session.get("passkey",{}).get("name"),"testKey")




