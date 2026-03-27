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

    def test_expired_state_token(self):
        from unittest.mock import patch
        from django.core import signing
        # Register a key first to get a valid state_token format
        response = self.client.post('/api/passkeys/register/options')
        data = response.json()
        # Patch signing.loads to raise SignatureExpired
        with patch('passkeys.api.service.signing.loads', side_effect=signing.SignatureExpired('expired')):
            response = self.client.post('/api/passkeys/register/verify', {
                'state_token': data['state_token'],
                'credential': {'id': 'fake'},
            }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_auth_expired_state_token(self):
        from unittest.mock import patch
        from django.core import signing
        with patch('passkeys.api.service.signing.loads', side_effect=signing.SignatureExpired('expired')):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': 'expired-token',
                'credential': {'id': 'fake'},
            }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_auth_missing_credential_id(self):
        from unittest.mock import patch
        self.client.force_authenticate(user=None)
        with patch('passkeys.api.service.signing.loads', return_value={}):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': 'valid-token',
                'credential': {},
            }, format='json')
        self.assertIn(response.status_code, [401, 403])

    def test_auth_passkey_not_found(self):
        from unittest.mock import patch
        with patch('passkeys.api.service.signing.loads', return_value={}):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': 'valid-token',
                'credential': {'id': 'nonexistent-credential-id'},
            }, format='json')
        self.assertEqual(response.status_code, 404)

    def test_duplicate_passkey_registration(self):
        from unittest.mock import patch
        from django.db import IntegrityError
        device = self._register_key()
        # Try registering again - mock IntegrityError on save
        response = self.client.post('/api/passkeys/register/options')
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        device2 = SoftWebauthnDevice()
        credential = device2.create(options, "https://" + options["publicKey"]["rp"]["id"])
        with patch('passkeys.webauthn.UserPasskey.save', side_effect=IntegrityError):
            response = self.client.post('/api/passkeys/register/verify', {
                'state_token': data['state_token'],
                'key_name': 'dup',
                'credential': credential,
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

    def test_reg_verify_generic_exception(self):
        from unittest.mock import patch
        response = self.client.post('/api/passkeys/register/options')
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        device = SoftWebauthnDevice()
        credential = device.create(options, "https://" + options["publicKey"]["rp"]["id"])
        with patch('passkeys.api.service.complete_registration', side_effect=RuntimeError('fido2 error')):
            response = self.client.post('/api/passkeys/register/verify', {
                'state_token': data['state_token'],
                'key_name': 'test',
                'credential': credential,
            }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_auth_bad_signature_state_token(self):
        response = self.client.post('/api/passkeys/authenticate/verify', {
            'state_token': 'tampered-bad-signature-token',
            'credential': {'id': 'fake'},
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_auth_verify_value_error(self):
        from unittest.mock import patch
        with patch('passkeys.api.service.signing.loads', return_value={}):
            with patch('passkeys.api.service.complete_authentication', side_effect=ValueError('bad')):
                response = self.client.post('/api/passkeys/authenticate/verify', {
                    'state_token': 'valid',
                    'credential': {'id': 'some-id'},
                }, format='json')
        self.assertIn(response.status_code, [400, 401, 403])

    def test_auth_begin_uses_authenticated_user(self):
        """auth_begin_service should use request.user.get_username() when no username provided."""
        device = self._register_key()
        # Don't logout - stay authenticated
        response = self.client.post('/api/passkeys/authenticate/options', {}, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should have allowCredentials since it found the authenticated user's keys
        self.assertIn('options', data)

    def test_session_token_backend_directly(self):
        from passkeys.api.token_backends import _session_token_backend
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/')
        from django.contrib.sessions.backends.file import SessionStore
        request.session = SessionStore()
        result = _session_token_backend(self.user, request)
        self.assertEqual(result['token_type'], 'session')

    def test_custom_token_backend(self):
        from unittest.mock import patch
        device = self._register_key()
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/passkeys/authenticate/options', {}, format='json')
        data = response.json()
        options = data['options']
        options['publicKey']['challenge'] = options['publicKey']['challenge'].encode("ascii")
        assertion = device.get(options, "https://" + options["publicKey"]["rpId"])

        mock_token_response = {'token_type': 'custom', 'token': 'custom-token'}
        with patch('passkeys.api.views.get_token_response', return_value=mock_token_response):
            response = self.client.post('/api/passkeys/authenticate/verify', {
                'state_token': data['state_token'],
                'credential': assertion,
            }, format='json', HTTP_USER_AGENT="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token_type'], 'custom')

    def test_load_custom_backend_setting(self):
        from unittest.mock import patch
        from passkeys.api.token_backends import get_token_response
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/')
        from django.contrib.sessions.backends.file import SessionStore
        request.session = SessionStore()

        def my_backend(user, request):
            return {'token_type': 'my_custom', 'key': '123'}

        with patch.object(settings, 'PASSKEYS_API_TOKEN_BACKEND', 'test_app.tests.test_api.my_custom_backend', create=True):
            with patch('passkeys.api.token_backends._load_custom_backend', return_value=my_backend):
                result = get_token_response(self.user, request)
        self.assertEqual(result['token_type'], 'my_custom')

    def test_load_custom_backend_import_error(self):
        from passkeys.api.token_backends import _load_custom_backend
        from django.core.exceptions import ImproperlyConfigured
        with self.assertRaises(ImproperlyConfigured):
            _load_custom_backend('nonexistent.module.backend')

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
