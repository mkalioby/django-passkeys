import json
from base64 import urlsafe_b64encode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import reverse

from passkeys.models import UserPasskey
from .softwebauthn import SoftWebauthnDevice

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"

PLATFORM = "Safari / Mac OS X"

def get_server_id(request):
    return "fido-server-id-callable"


def get_server_name(request):
    return "fido-server-name-callable"


class FidoTestCase(TransactionTestCase):
    def setUp(self) -> None:
        settings.FIDO_SERVER_ID = get_server_id
        settings.FIDO_SERVER_NAME = get_server_name

        self.user_model = get_user_model()
        self.user_model.objects.create_user(username="a", password="a")
        self.user_model.objects.create_user(username="b", password="b")

    def test_server_id_callable(self):
        self.client.logout()
        settings.FIDO_SERVER_ID = get_server_id
        response = self.client.get(reverse('passkeys:auth_begin'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['publicKey']['rpId'], 'fido-server-id-callable')

    def test_server_name_callable(self):
        self.client.login(username="b", password="b")
        response = self.client.get(reverse('passkeys:reg_begin'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['publicKey']['rp']["name"], 'fido-server-name-callable')
        self.client.logout()

    def __test_registration(self, key_name=None):
        # check login
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
        self.assertEqual(key.user.username, "b")

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
