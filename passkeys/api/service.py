import logging
from base64 import urlsafe_b64encode

from django.conf import settings
from django.core import signing
from django.db import IntegrityError
from django.utils import timezone
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import AttestedCredentialData

from passkeys.models import UserPasskey
from passkeys.FIDO2 import getServer, getUserCredentials, get_current_platform as _get_current_platform, enable_json_mapping

logger = logging.getLogger(__name__)

STATE_TOKEN_MAX_AGE = 300  # 5 minutes
STATE_TOKEN_SALT = 'passkeys.api.fido2_state'


def get_current_platform_safe(request):
    """Wrapper that handles missing HTTP_USER_AGENT header."""
    if not request.META.get("HTTP_USER_AGENT"):
        return "Key"
    return _get_current_platform(request)


class PasskeyStateError(Exception):
    pass


class PasskeyVerificationError(Exception):
    pass


class PasskeyNotFoundError(Exception):
    pass


def reg_begin_service(user, request):
    import fido2.webauthn

    enable_json_mapping()
    server = getServer(request)
    auth_attachment = getattr(settings, 'KEY_ATTACHMENT', None)
    registration_data, state = server.register_begin(
        {
            'id': urlsafe_b64encode(user.get_username().encode('utf8')),
            'name': user.get_username(),
            'displayName': user.get_full_name(),
        },
        getUserCredentials(user.get_username()),
        authenticator_attachment=auth_attachment,
        resident_key_requirement=fido2.webauthn.ResidentKeyRequirement.PREFERRED,
    )
    if hasattr(request, 'session'):
        request.session['fido2_state'] = state

    state_token = signing.dumps(state, salt=STATE_TOKEN_SALT)
    return {'options': dict(registration_data), 'state_token': state_token}


def reg_complete_service(user, state_token, credential, key_name, request):
    try:
        state = signing.loads(state_token, salt=STATE_TOKEN_SALT, max_age=STATE_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise PasskeyStateError("Registration state has expired, please try again")
    except signing.BadSignature:
        raise PasskeyStateError("Invalid registration state token")

    enable_json_mapping()
    server = getServer(request)
    try:
        auth_data = server.register_complete(state, response=credential)
    except Exception:
        logger.exception("Passkey registration verification failed")
        raise PasskeyVerificationError("Passkey verification failed, please try again")

    encoded = websafe_encode(auth_data.credential_data)
    platform = get_current_platform_safe(request)
    name = key_name or platform

    passkey = UserPasskey(
        user=user,
        token=encoded,
        name=name,
        platform=platform,
    )
    if credential.get('id'):
        passkey.credential_id = credential['id']

    try:
        passkey.save()
    except IntegrityError:
        raise PasskeyVerificationError("This passkey is already registered")

    return passkey


def auth_begin_service(username, request):
    enable_json_mapping()
    server = getServer(request)
    credentials = []

    if not username and hasattr(request, 'session'):
        username = request.session.get('base_username')
    if not username and hasattr(request, 'user') and request.user.is_authenticated:
        username = request.user.get_username()

    if username:
        credentials = getUserCredentials(username)

    auth_data, state = server.authenticate_begin(credentials)

    if hasattr(request, 'session'):
        request.session['fido2_state'] = state

    state_token = signing.dumps(state, salt=STATE_TOKEN_SALT)
    return {'options': dict(auth_data), 'state_token': state_token}


def auth_complete_service(state_token, credential, request):
    try:
        state = signing.loads(state_token, salt=STATE_TOKEN_SALT, max_age=STATE_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise PasskeyStateError("Authentication state has expired, please try again")
    except signing.BadSignature:
        raise PasskeyStateError("Invalid authentication state token")

    credential_id = credential.get('id')
    if not credential_id:
        raise PasskeyVerificationError("Missing credential id")

    key = UserPasskey.objects.filter(credential_id=credential_id, enabled=True).first()
    if key is None:
        raise PasskeyNotFoundError("Passkey not found or disabled")

    credentials = [AttestedCredentialData(websafe_decode(key.token))]
    enable_json_mapping()
    server = getServer(request)

    try:
        server.authenticate_complete(state, credentials=credentials, response=credential)
    except ValueError:
        raise PasskeyVerificationError("Passkey authentication failed")

    key.last_used = timezone.now()
    key.save(update_fields=['last_used'])

    if hasattr(request, 'session'):
        request.session['passkey'] = {
            'passkey': True,
            'name': key.name,
            'id': key.id,
            'platform': key.platform,
            'cross_platform': get_current_platform_safe(request) != key.platform,
        }

    return key.user
