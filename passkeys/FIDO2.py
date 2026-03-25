import json
import traceback

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from passkeys.webauthn import begin_registration, complete_registration, begin_authentication, complete_authentication


# ── View functions (Django template flow) ──

def reg_begin(request):
    """Starts registering a new FIDO Device, called from API"""
    registration_data, state = begin_registration(request.user, request)
    request.session['fido2_state'] = state
    return JsonResponse(registration_data)

@login_required
@csrf_exempt
def reg_complete(request):
    """Completes the registration, called by API"""
    try:
        if not "fido2_state" in request.session:
            return JsonResponse({'status': 'ERR', "message": "FIDO Status can't be found, please try again"})
        data = json.loads(request.body)
        state = request.session.pop("fido2_state")
        complete_registration(state, data, request.user, request)
        return JsonResponse({'status': 'OK'})
    except Exception as exp: # pragma: no cover
        print(traceback.format_exc()) # pragma: no cover
        return JsonResponse({'status': 'ERR', "message": "Error on server, please try again later"}) # pragma: no cover


def auth_begin(request):
    username = None
    if "base_username" in request.session:
        username = request.session["base_username"]
    if request.user.is_authenticated:
        username = request.user.get_username()
    auth_data, state = begin_authentication(username, request)
    request.session['fido2_state'] = state
    return JsonResponse(auth_data)


@csrf_exempt
def auth_complete(request):
    data = json.loads(request.POST["passkeys"])
    state = request.session.pop('fido2_state')
    return complete_authentication(state, data, request)