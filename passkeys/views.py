import json
from base64 import urlsafe_b64encode

import fido2.features
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from fido2.utils import websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity

from .models import UserPasskey
from .util import getServer, enable_json_mapping, getUserCredentials, get_current_platform


#
# AUTHENTICATION
#

def auth_begin(request):
    enable_json_mapping()
    server = getServer(request)
    credentials = []
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


#
# KEY REGISTRATION
#
@login_required
def reg_begin(request):
    """Starts registering a new FIDO Device, called from API"""
    enable_json_mapping()
    server = getServer(request)
    auth_attachment = getattr(settings, 'KEY_ATTACHMENT', None)

    registration_data, state = server.register_begin(
        {
            u'id': urlsafe_b64encode(request.user.username.encode("utf8")),
            u'name': request.user.get_username(),
            u'displayName': request.user.get_full_name()
        },
        getUserCredentials(request.user),
        authenticator_attachment=auth_attachment,
        resident_key_requirement=fido2.webauthn.ResidentKeyRequirement.PREFERRED
    )

    request.session['fido2_state'] = state

    return JsonResponse(dict(registration_data))


@login_required
@csrf_exempt
def reg_complete(request):
    """Completes the registration, called by API"""
    try:
        if "fido2_state" not in request.session:
            return JsonResponse(
                {'status': 'ERR', "message": "FIDO Status can't be found, please try again"},
                status=401
            )

        enable_json_mapping()
        data = json.loads(request.body)
        name = data.pop("key_name", '')
        server = getServer(request)
        auth_data = server.register_complete(request.session.pop("fido2_state"), response=data)
        encoded = websafe_encode(auth_data.credential_data)
        platform = get_current_platform(request)

        if name == "":
            name = platform

        uk = UserPasskey(user=request.user, token=encoded, name=name, platform=platform)

        if data.get("id"):
            uk.credential_id = data.get('id')

        uk.save()

        return JsonResponse({'status': 'OK'})
    except:
        return JsonResponse(
            {'status': 'ERR', "message": "Error on server, please try again later"},
            status=500
        )


#
# KEY MANAGEMENT
#

@login_required
def index(request):
    keys = UserPasskey.objects.filter(user=request.user)  # pragma: no cover
    return render(request, 'passkeys/passkeys.html', {"keys": keys})  # pragma: no cover


@login_required
@require_http_methods(["DELETE"])
def delete(request, pk):
    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("", status=400)

    key.delete()

    return HttpResponse("")


@require_http_methods(["POST"])
@login_required
def toggle(request, pk):
    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("", status=400)

    key.enabled = not key.enabled
    key.save()

    return HttpResponse("")
