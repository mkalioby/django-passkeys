import fido2.features
from django.conf import settings
from django.contrib.auth import get_user_model
from fido2.server import Fido2Server
from fido2.utils import websafe_decode
from fido2.webauthn import PublicKeyCredentialRpEntity, AttestedCredentialData
from user_agents.parsers import parse as ua_parse

from .models import UserPasskey


def enable_json_mapping():
    try:
        fido2.features.webauthn_json_mapping.enabled = True
    except:
        pass


def getUserCredentials(user):
    User = get_user_model()
    username_field = User.USERNAME_FIELD
    filter_args = {"user__" + username_field: user}
    return [AttestedCredentialData(websafe_decode(uk.token)) for uk in UserPasskey.objects.filter(**filter_args)]


def getServer(request=None):
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


def get_current_platform(request):
    ua = ua_parse(request.META["HTTP_USER_AGENT"])
    return f'{ua.browser.family} / {ua.os.family}'
