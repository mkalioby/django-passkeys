import json
from base64 import urlsafe_b64encode
import traceback

import fido2.features
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity, AttestedCredentialData, RegistrationResponse
from .models import UserPasskey
from user_agents.parsers import parse as ua_parse


def enable_json_mapping():
    try:
        fido2.features.webauthn_json_mapping.enabled = True
    except:
        pass


def getUserCredentials(user):
    User = get_user_model()
    username_field = User.USERNAME_FIELD
    filter_args = {"user__"+username_field : user}
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
    if 'Safari' in ua.browser.family:
        return "Apple"
    elif 'Chrome' in ua.browser.family and ua.os.family == "Mac OS X":
        return "Chrome on Apple"
    elif 'Android' in ua.os.family:
        return "Google"
    elif "Windows" in ua.os.family:
        return "Microsoft"
    else: return "Key"


def reg_begin(request):
    """Starts registering a new FIDO Device, called from API"""
    enable_json_mapping()
    server = getServer(request)
    auth_attachment = getattr(settings,'KEY_ATTACHMENT', None)
    registration_data, state = server.register_begin({
        u'id':  urlsafe_b64encode(request.user.username.encode("utf8")),
        u'name': request.user.get_username(),
        u'displayName': request.user.get_full_name()
    }, getUserCredentials(request.user), authenticator_attachment = auth_attachment, resident_key_requirement=fido2.webauthn.ResidentKeyRequirement.PREFERRED)
    request.session['fido2_state'] = state
    return JsonResponse(dict(registration_data))
    #return HttpResponse(cbor.encode(registration_data), content_type = 'application/octet-stream')


@csrf_exempt
def reg_complete(request):
    """Completes the registeration, called by API"""
    try:
        if not "fido2_state" in request.session:
            return JsonResponse({'status': 'ERR', "message": "FIDO Status can't be found, please try again"})
        enable_json_mapping()
        data = json.loads(request.body)
        name = data.pop("key_name",'')
        server = getServer(request)
        auth_data = server.register_complete(request.session.pop("fido2_state"), response = data)
        encoded = websafe_encode(auth_data.credential_data)
        platform = get_current_platform(request)
        if name == "":
            name = platform
        uk = UserPasskey(user=request.user, token=encoded, name = name,platform=platform)
        if data.get("id"):
            uk.credential_id = data.get('id')

        uk.save()
        return JsonResponse({'status': 'OK'})
    except Exception as exp: # pragma: no cover
        print(traceback.format_exc()) # pragma: no cover
        return JsonResponse({'status': 'ERR', "message": "Error on server, please try again later"}) # pragma: no cover


def auth_begin(request):
    enable_json_mapping()
    server = getServer(request)
    credentials=[]
    username = None
    if "base_username" in request.session:
        username = request.session["base_username"]
    if request.user.is_authenticated:
        username = request.user.username
    if username:
        credentials = getUserCredentials(username)
    auth_data, state = server.authenticate_begin(credentials)
    request.session['fido2_state'] = state
    return JsonResponse(dict(auth_data))


@csrf_exempt
def auth_complete(request):
    enable_json_mapping()
    credentials = []
    server = getServer(request)
    data = json.loads(request.POST["passkeys"])
    key = None
    #userHandle = data.get("response",{}).get('userHandle')
    credential_id = data['id']
    #
    # if userHandle:
    #     if User_Passkey.objects.filter(=userHandle).exists():
    #         credentials = getUserCredentials(userHandle)
    #         username=userHandle
    #     else:
    #         keys = User_Keys.objects.filter(user_handle = userHandle)
    #         if keys.exists():
    #             credentials = [AttestedCredentialData(websafe_decode(keys[0].properties["device"]))]

    keys = UserPasskey.objects.filter(credential_id = credential_id,enabled=1)
    if keys.exists():

        credentials=[AttestedCredentialData(websafe_decode(keys[0].token))]
        key = keys[0]

        try:
            cred = server.authenticate_complete(
                    request.session.pop('fido2_state'), credentials = credentials, response = data
            )
        except ValueError:   # pragma: no cover
            return None      # pragma: no cover
        except Exception as excep:              # pragma: no cover
            raise Exception(excep)              # pragma: no cover
        if key:
            key.last_used = timezone.now()
            request.session["passkey"] = {'passkey': True, 'name': key.name, "id":key.id, "platform": key.platform,
                                           'cross_platform': get_current_platform(request) != key.platform}
            key.save()
            return key.user
    return None                           # pragma: no cover
