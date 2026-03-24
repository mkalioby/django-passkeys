from importlib import import_module

from django.conf import settings
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from passkeys.models import UserPasskey
from test_app.soft_webauthn import SoftWebauthnDevice


class TestPasskeyAPI(TransactionTestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user_model = get_user_model()
        if self.user_model.objects.filter(username="test").exists():
            self.user = self.user_model.objects.get(username="test")
        else:
            self.user = self.user_model.objects.create_user(username="test", password="test")

        self.client = APIClient()

        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save(must_create=True)
        self.session = store
        self.client.cookies["sessionid"] = store.session_key

        self.client.force_authenticate(user=self.user)

    def _register_key(self, key_name="testKey", **extra):
        response = self.client.post('/api/passkeys/register/options', **extra)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('state_token', data)
        self.assertIn('options', data)

        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")

        device = SoftWebauthnDevice()
        credential = device.create(options, "https://" + options["publicKey"]["rp"]["id"])

        response = self.client.post('/api/passkeys/register/verify', {
            'state_token': data['state_token'],
            'key_name': key_name,
            'credential': credential,
        }, format='json', **extra)
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result['name'], key_name)
        return device

    def test_register_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/passkeys/register/options')
        self.assertIn(response.status_code, [401, 403])

    def test_registration_flow(self):
        self._register_key()
        self.assertTrue(UserPasskey.objects.filter(name="testKey").exists())

    def test_auto_key_name(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
        response = self.client.post('/api/passkeys/register/options', HTTP_USER_AGENT=ua)
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")

        device = SoftWebauthnDevice()
        credential = device.create(options, "https://" + options["publicKey"]["rp"]["id"])

        response = self.client.post('/api/passkeys/register/verify', {
            'state_token': data['state_token'],
            'key_name': '',
            'credential': credential,
        }, format='json', HTTP_USER_AGENT=ua)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Apple')

    def test_list_passkeys(self):
        self._register_key("key1")
        self._register_key("key2")
        response = self.client.get('/api/passkeys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_list_only_own_keys(self):
        self._register_key("my_key")
        other_user = self.user_model.objects.create_user(username="other", password="other")
        self.client.force_authenticate(user=other_user)
        response = self.client.get('/api/passkeys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_delete_passkey(self):
        self._register_key()
        key = UserPasskey.objects.filter(user=self.user).latest('id')
        response = self.client.delete(f'/api/passkeys/{key.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(UserPasskey.objects.filter(id=key.id).exists())

    def test_delete_other_users_key_returns_404(self):
        self._register_key()
        key = UserPasskey.objects.filter(user=self.user).latest('id')
        other_user = self.user_model.objects.create_user(username="other2", password="other2")
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(f'/api/passkeys/{key.id}')
        self.assertEqual(response.status_code, 404)

    def test_update_passkey(self):
        self._register_key()
        key = UserPasskey.objects.filter(user=self.user).latest('id')
        self.assertTrue(key.enabled)

        response = self.client.patch(f'/api/passkeys/{key.id}', {'enabled': False}, format='json')
        self.assertEqual(response.status_code, 200)
        key.refresh_from_db()
        self.assertFalse(key.enabled)

        response = self.client.patch(f'/api/passkeys/{key.id}', {'name': 'My Laptop', 'enabled': True}, format='json')
        self.assertEqual(response.status_code, 200)
        key.refresh_from_db()
        self.assertTrue(key.enabled)
        self.assertEqual(key.name, 'My Laptop')

    def test_authenticate_flow_with_session(self):
        device = self._register_key()
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/passkeys/authenticate/options', {}, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('state_token', data)

        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        assertion = device.get(options, "https://" + options["publicKey"]["rpId"])

        response = self.client.post('/api/passkeys/authenticate/verify', {
            'state_token': data['state_token'],
            'credential': assertion,
        }, format='json', HTTP_USER_AGENT="")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['username'], 'test')
        self.assertEqual(result['token_type'], 'session')

    def test_authenticate_options_with_username(self):
        device = self._register_key()
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/passkeys/authenticate/options', {'username': 'test'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('options', response.json())

    def test_invalid_state_token(self):
        response = self.client.post('/api/passkeys/register/verify', {
            'state_token': 'invalid-token',
            'credential': {},
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_authenticate_with_drf_token_backend(self):
        from unittest.mock import patch
        device = self._register_key()
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/passkeys/authenticate/options', {}, format='json')
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        assertion = device.get(options, "https://" + options["publicKey"]["rpId"])

        mock_token_response = {'token_type': 'token', 'token': 'fake-token-key'}
        with patch('passkeys.api.views.get_token_response', return_value=mock_token_response):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': data['state_token'],
                'credential': assertion,
            }, format='json', HTTP_USER_AGENT="")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['token_type'], 'token')
        self.assertEqual(result['token'], 'fake-token-key')

    def test_authenticate_with_jwt_token_backend(self):
        from unittest.mock import patch
        device = self._register_key()
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/passkeys/authenticate/options', {}, format='json')
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        assertion = device.get(options, "https://" + options["publicKey"]["rpId"])

        mock_token_response = {'token_type': 'jwt', 'access': 'fake-access', 'refresh': 'fake-refresh'}
        with patch('passkeys.api.views.get_token_response', return_value=mock_token_response):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': data['state_token'],
                'credential': assertion,
            }, format='json', HTTP_USER_AGENT="")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['token_type'], 'jwt')
        self.assertEqual(result['access'], 'fake-access')
        self.assertEqual(result['refresh'], 'fake-refresh')
