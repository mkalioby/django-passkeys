import logging

from django.core import signing
from django.db import IntegrityError

from passkeys.webauthn import (
    begin_registration,
    complete_registration,
    begin_authentication,
    complete_authentication,
)

logger = logging.getLogger(__name__)

STATE_TOKEN_MAX_AGE = 300  # 5 minutes
STATE_TOKEN_SALT = 'passkeys.api.fido2_state'


class PasskeyStateError(Exception):
    pass


class PasskeyVerificationError(Exception):
    pass


class PasskeyNotFoundError(Exception):
    pass


def reg_begin_service(user, request):
    registration_data, state = begin_registration(user, request)

    if hasattr(request, 'session'):
        request.session['fido2_state'] = state

    state_token = signing.dumps(state, salt=STATE_TOKEN_SALT)
    return {'options': registration_data, 'state_token': state_token}


def reg_complete_service(user, state_token, credential, key_name, request):
    try:
        state = signing.loads(state_token, salt=STATE_TOKEN_SALT, max_age=STATE_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise PasskeyStateError("Registration state has expired, please try again")
    except signing.BadSignature:
        raise PasskeyStateError("Invalid registration state token")

    credential['key_name'] = key_name

    try:
        passkey = complete_registration(state, credential, user, request)
    except IntegrityError:
        raise PasskeyVerificationError("This passkey is already registered")
    except Exception:
        logger.exception("Passkey registration verification failed")
        raise PasskeyVerificationError("Passkey verification failed, please try again")

    return passkey


def auth_begin_service(username, request):
    if not username and hasattr(request, 'session'):
        username = request.session.get('base_username')
    if not username and hasattr(request, 'user') and request.user.is_authenticated:
        username = request.user.get_username()

    auth_data, state = begin_authentication(username, request)

    if hasattr(request, 'session'):
        request.session['fido2_state'] = state

    state_token = signing.dumps(state, salt=STATE_TOKEN_SALT)
    return {'options': auth_data, 'state_token': state_token}


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

    try:
        user = complete_authentication(state, credential, request)
    except ValueError:
        raise PasskeyVerificationError("Passkey authentication failed")

    if user is None:
        raise PasskeyNotFoundError("Passkey not found or disabled")

    return user