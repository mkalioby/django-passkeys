import json
from base64 import urlsafe_b64encode
from importlib import import_module

from django.http import HttpRequest
from django.test import RequestFactory,TransactionTestCase, Client
from django.urls import reverse

from django.conf import settings
from test_app.soft_webauthn import SoftWebauthnDevice

from passkeys.models import UserPasskey


def get_server_id(request):
    return request.META["SERVER_NAME"] + "1"

def get_server_name(request):
    return "MySite"

class test_fido(TransactionTestCase):
    def setUp(self) -> None:
        if not getattr(self,"assertEquals",None):
            self.assertEquals = self.assertEqual
        from django.contrib.auth import get_user_model
        self.user_model = get_user_model()
        if self.user_model.objects.filter(username="test").count()==0:
            self.user = self.user_model.objects.create_user(username="test",password="test")
        else:
            self.user = self.user_model.objects.get(username="test")
        self.client = Client()
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        #settings.SESSION_FILE_PATH = "/"
        store = engine.SessionStore()
        store.save(must_create=True)
        self.session = store
        self.client.cookies["sessionid"] = store.session_key

        self.client.post("/auth/login", {"username": "test", "password": "test", 'passkeys': ''})
        self.factory = RequestFactory()


    def test_key_reg(self):
        self.client.post('auth/login',{"usernaame":"test","password":"test","passkeys":""})
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
        self.assertEquals(UserPasskey.objects.latest('id').name, "testKey")
        return s


    def test_auto_key_name(self):
        r = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        j['publicKey']['challenge'] = j['publicKey']['challenge'].encode("ascii")
        s = SoftWebauthnDevice()
        res = s.create(j, "https://" + j["publicKey"]["rp"]["id"])
        u = reverse('passkeys:reg_complete')
        r = self.client.post(u, data=json.dumps(res), HTTP_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15", content_type="application/json")
        try:
            j = json.loads(r.content)
        except Exception:
            raise AssertionError("Failed to get the required JSON after reg_completed")
        self.assertTrue("status" in j)
        self.assertEquals(j["status"], "OK")
        self.assertEquals(UserPasskey.objects.latest('id').name,"Apple")
        return s

    def test_error_when_no_session(self):
        res = {}
        res["key_name"] = "testKey"
        u = reverse('passkeys:reg_complete')
        r = self.client.post(u, data=json.dumps(res), headers={"USER_AGENT": ""}, HTTP_USER_AGENT="",
                             content_type="application/json")
        try:
            j = json.loads(r.content)
        except Exception:
            raise AssertionError("Failed to get the required JSON after reg_completed")
        self.assertTrue("status" in j)
        self.assertEquals(j["status"], "ERR")
        self.assertEquals(j["message"], "FIDO Status can't be found, please try again")

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

    def test_base_username(self):
        authenticator = self.test_key_reg()
        self.client.get('/auth/logout')
        session = self.session
        session["base_username"]= "test"
        session.save(must_create=True)
        self.client.cookies["sessionid"] = session.session_key
        r = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEquals(j['publicKey']['allowCredentials'][0]['id'],urlsafe_b64encode(authenticator.credential_id).decode("utf8").strip('='))

    def test_passkey_login_no_session(self):
        pass


    def test_server_id_callable(self):
        from test_app.tests.test_fido import get_server_id
        settings.FIDO_SERVER_ID = get_server_id
        r = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEquals(j['publicKey']['rpId'],'testserver1')

    def test_server_name_callable(self):
        from test_app.tests.test_fido import get_server_name
        settings.FIDO_SERVER_NAME = get_server_name
        r = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEquals(r.status_code, 200)
        j = json.loads(r.content)
        self.assertEquals(j['publicKey']['rp']["name"],'MySite')
