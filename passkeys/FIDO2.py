import json

import fido2.features
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from fido2.server import Fido2Server
from fido2.utils import websafe_decode, websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity, AttestedCredentialData, RegistrationResponse
from .models import UserPasskey


def enable_json_mapping():
    try:
        fido2.features.webauthn_json_mapping.enabled = True
    except:
        pass

def getUserCredentials(user):
    return [AttestedCredentialData(websafe_decode(uk.token)) for uk in UserPasskey.objects.filter(user = user)]



def getServer():
    """Get Server Info from settings and returns a Fido2Server"""
    rp = PublicKeyCredentialRpEntity(id=settings.FIDO_SERVER_ID, name=settings.FIDO_SERVER_NAME)
    return Fido2Server(rp)


def reg_begin(request):
    """Starts registering a new FIDO Device, called from API"""
    enable_json_mapping()
    server = getServer()
    auth_attachment = getattr(settings,'KEY_ATTACHMENT', None)
    registration_data, state = server.register_begin({
        u'id': request.user.username.encode("utf8"),
        u'name': request.user.username,
        u'displayName': request.user.username,
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
        server = getServer()
        auth_data = server.register_complete(request.session.pop("fido2_state"), response = data)
        encoded = websafe_encode(auth_data.credential_data)
        uk = UserPasskey(user=request.user, token=encoded, name = name)
        if data.get("id"):
            uk.credential_id = data.get('id')
        #TODO: Detect the key platform
        uk.save()
        return JsonResponse({'status': 'OK'})
    except Exception as exp:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'ERR', "message": "Error on server, please try again later"})







def auth_begin(request):
    enable_json_mapping()
    server = getServer()
    credentials=[]
    username = None
    if "base_username" in request.session:
        username = request.session["base_username"]
    if request.user.is_authenticated:
        username = request.user.username
    if username:
        credentials = getUserCredentials(request.session.get("base_username", request.user.username))
    auth_data, state = server.authenticate_begin(credentials)
    request.session['fido2_state'] = state
    return JsonResponse(dict(auth_data))



@csrf_exempt
def auth_complete(request):
    enable_json_mapping()
    credentials = []
    server = getServer()
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

    keys = UserPasskey.objects.filter(credential_id = credential_id)
    if keys.exists():
        credentials=[AttestedCredentialData(websafe_decode(keys[0].token))]
        key = keys[0]

        try:
            cred = server.authenticate_complete(
                    request.session.pop('fido2_state'), credentials = credentials, response = data
            )
        except ValueError:
            return None
        except Exception as excep:
            raise Exception(excep)
        if key:
            key.last_used = timezone.now()
            key.save()
            return key.user
    return None