import json
from base64 import urlsafe_b64encode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TransactionTestCase
from django.urls import reverse

from passkeys.backend import PasskeyModelBackend
from passkeys.models import UserPasskey
from passkeys.tests.soft_webauthn import SoftWebauthnDevice

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"

PLATFORM = "Apple"


def get_server_id(request):
    return "fido-server-id"


def get_server_name(request):
    return "fido-server-name"


class FidoTestCase(TransactionTestCase):
    def setUp(self) -> None:
        settings.FIDO_SERVER_ID = get_server_id
        settings.FIDO_SERVER_NAME = get_server_name

        self.user_model = get_user_model()
        self.user_a = self.user_model.objects.create_user(username="a", password="a")
        self.user_b = self.user_model.objects.create_user(username="b", password="b")

    def test_server_id_callable(self):
        self.client.logout()
        settings.FIDO_SERVER_ID = get_server_id
        response = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['publicKey']['rpId'], 'fido-server-id')

    def test_server_name_callable(self):
        self.client.login(username="b", password="b")
        response = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['publicKey']['rp']["name"], 'fido-server-name')
        self.client.logout()

    def __test_registration(self, key_name=None):
        # make sure no keys exist
        UserPasskey.objects.all().delete()

        # check anonymous access
        response = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('passkeys:reg_complete'))
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username="b", password="b")

        # start registration
        response = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        data['publicKey']['challenge'] = data['publicKey']['challenge'].encode("ascii")

        # creqte authentication data
        authenticator = SoftWebauthnDevice()

        request = authenticator.create(data, "https://" + data["publicKey"]["rp"]["id"])
        if key_name is not None:
            request["key_name"] = key_name

        # complete registration
        response = self.client.post(
            reverse('passkeys:reg_complete'),
            data=json.dumps(request),
            headers={"USER_AGENT": USER_AGENT},
            HTTP_USER_AGENT=USER_AGENT,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        key = UserPasskey.objects.latest('id')
        self.assertNotEqual(key, None)

        if key_name is None:
            self.assertEqual(key.name, key.platform)
        else:
            self.assertEqual(key.name, key_name)

        self.assertEqual(key.platform, PLATFORM)
        self.assertEqual(key.user, self.user_b)

        return authenticator

    def test_registration(self):
        self.__test_registration('test-key')

    def test_registration_auto_key_name(self):
        self.__test_registration()

    def test_base_username(self):
        authenticator = self.__test_registration()

        self.client.logout()

        session = self.client.session
        session.update({"base_username": "b"})
        session.save()

        response = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json()['publicKey']['allowCredentials'][0]['id'],
                         urlsafe_b64encode(authenticator.credential_id).decode("utf8").strip('='))

    def test_error_when_no_session(self):
        self.client.login(username='a', password='a')
        res = {"key_name": "testKey"}
        url = reverse('passkeys:reg_complete')
        r = self.client.post(url, data=json.dumps(res), headers={"USER_AGENT": ""}, HTTP_USER_AGENT="",
                             content_type="application/json")
        try:
            j = json.loads(r.content)
        except Exception:
            raise AssertionError("Failed to get the required JSON after reg_completed")

        self.assertTrue("status" in j)
        self.assertEqual(j["status"], "ERR")
        self.assertEqual(j["message"], "FIDO Status can't be found, please try again")

    def test_passkey_login(self):
        authenticator = self.__test_registration("TestKey")
        self.client.logout()

        response = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEqual(response.status_code, 200)
        result = response.json()
        result['publicKey']['challenge'] = result['publicKey']['challenge'].encode("ascii")

        res = authenticator.get(result, "https://" + result["publicKey"]["rpId"])

        factory = RequestFactory()
        request = factory.post('/login/',
                               {
                                   "username": "",
                                   "password": "",
                                   'passkeys': json.dumps(res)
                               },
                               headers={"USER_AGENT": USER_AGENT})
        request.session = self.client.session

        backend = PasskeyModelBackend()
        user = backend.authenticate(request, "", "")

        self.assertEqual(user, self.user_b)
        self.assertTrue(self.client.session.get("passkey", {}).get("passkey", True))
        self.assertEqual(self.client.session.get("passkey", {}).get("name"), "TestKey")
