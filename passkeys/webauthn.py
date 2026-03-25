# ── Core functions (used by both views and API service layer) ──
import fido2.features
from base64 import urlsafe_b64encode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from .models import UserPasskey
from user_agents.parsers import parse as ua_parse

NEW_FIDO_VER = False
try:
    from importlib.metadata import version
    fido2_version = version('fido2')
    NEW_FIDO_VER = fido2_version.split(".")[0] > "1"
except Exception: # pragma: no cover
    NEW_FIDO_VER = fido2.__version__.split(".")[0] > "1"

def enable_json_mapping():
    if NEW_FIDO_VER:
        return
    try: # pragma: no cover
        if  hasattr(fido2.features,"webauthn_json_mapping"):
            fido2.features.webauthn_json_mapping.enabled = True
        else:
            raise Exception(
                "Failed to enable JSON mapping, please make sure you have fido2 version 1.0.0 or higher installed")

    except ValueError: # pragma: no cover
        pass


def getUserCredentials(user) -> list[AttestedCredentialData]:
    User = get_user_model()
    username_field = User.USERNAME_FIELD
    filter_args = {"user__"+username_field : user}
    return [AttestedCredentialData(websafe_decode(uk.token)) for uk in UserPasskey.objects.filter(**filter_args).only('token')]


def getServer(request=None) -> Fido2Server:
    """Get Server Info from settings and returns a Fido2Server"""
    if callable(settings.FIDO_SERVER_ID):
        fido_server_id = settings.FIDO_SERVER_ID(request)
    else:
        fido_server_id = settings.FIDO_SERVER_ID

    if callable(settings.FIDO_SERVER_NAME):
        fido_server_name = settings.FIDO_SERVER_NAME(request)
    else:
        fido_server_name = settings.FIDO_SERVER_NAME

    rp = PublicKeyCredentialRpEntity(id=fido_server_id, name=fido_server_name)
    return Fido2Server(rp)


def get_current_platform(request) -> str:
    ua = ua_parse(request.META.get("HTTP_USER_AGENT"))
    if not ua: return "Key"
    if 'Safari' in ua.browser.family:
        return "Apple"
    elif 'Chrome' in ua.browser.family and ua.os.family == "Mac OS X":
        return "Chrome on Apple"
    elif 'Android' in ua.os.family:
        return "Google"
    elif "Windows" in ua.os.family:
        return "Microsoft"
    else: return "Key"



def begin_registration(user, request) -> tuple[dict, dict]:
    """Core registration begin logic. Returns (registration_data_dict, state)."""
    enable_json_mapping()
    server = getServer(request)
    auth_attachment = getattr(settings, 'KEY_ATTACHMENT', None)
    username = user.get_username()
    user_entity = PublicKeyCredentialUserEntity(
        id=urlsafe_b64encode(username.encode("utf8")),
        name=username,
        display_name=user.get_full_name(),
    )
    registration_data, state = server.register_begin(
        user_entity, getUserCredentials(user), authenticator_attachment=auth_attachment,
        resident_key_requirement=fido2.webauthn.ResidentKeyRequirement.PREFERRED)
    return dict(registration_data), state


def complete_registration(state, credential_data, user, request) -> UserPasskey:
    """Core registration complete logic. Returns UserPasskey instance."""
    enable_json_mapping()
    server = getServer(request)
    auth_data = server.register_complete(state, response=credential_data)
    encoded = websafe_encode(auth_data.credential_data)
    platform = get_current_platform(request)
    name = credential_data.pop("key_name", '') or platform
    uk = UserPasskey(user=user, token=encoded, name=name, platform=platform)
    if credential_data.get("id"):
        uk.credential_id = credential_data.get('id')
    uk.save()
    return uk


def begin_authentication(username, request):
    """Core authentication begin logic. Returns (auth_data_dict, state)."""
    enable_json_mapping()
    server = getServer(request)
    credentials = []
    if username:
        credentials = getUserCredentials(username)
    auth_data, state = server.authenticate_begin(credentials)
    return dict(auth_data), state


def complete_authentication(state, credential_data, request):
    """Core authentication complete logic. Returns User or None."""
    enable_json_mapping()
    server = getServer(request)
    credential_id = credential_data['id']

    keys = UserPasskey.objects.filter(credential_id=credential_id, enabled=1)
    if not keys.exists():
        return None  # pragma: no cover

    key = keys[0]
    credentials = [AttestedCredentialData(websafe_decode(key.token))]

    try:
        server.authenticate_complete(
            state, credentials=credentials, response=credential_data
        )
    except ValueError:   # pragma: no cover
        return None      # pragma: no cover
    except Exception as excep:              # pragma: no cover
        raise Exception(excep)              # pragma: no cover

    key.last_used = timezone.now()
    key.save(update_fields=['last_used'])
    request.session["passkey"] = {
        'passkey': True,
        'name': key.name,
        "id": key.id,
        "platform": key.platform,
        'cross_platform': get_current_platform(request) != key.platform,
    }
    return key.user
