import json

from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from fido2.utils import websafe_decode
from fido2.webauthn import AttestedCredentialData

from .util import enable_json_mapping, getServer, get_current_platform
from .models import UserPasskey


class PasskeyModelBackend(ModelBackend):

    def authenticate(self, request, username='', password='', **kwargs):
        if username != '' and password != '':
            if request is not None:
                request.session["passkey"] = {'passkey': False}
            return super().authenticate(request, username=username, password=password, **kwargs)

        if request is None:
            return None

        passkeys = request.POST.get('passkeys')
        if passkeys in (None, ''):
            return None

        enable_json_mapping()
        server = getServer(request)
        data = json.loads(request.POST["passkeys"])

        credential_id = data['id']

        key = UserPasskey.objects.filter(credential_id=credential_id, enabled=1).first()
        if key is None:
            return None

        credentials = [AttestedCredentialData(websafe_decode(key.token))]

        try:
            server.authenticate_complete(
                request.session.pop('fido2_state'), credentials=credentials, response=data
            )
        except ValueError:
            return None

        key.last_used = timezone.now()
        key.save()

        request.session["passkey"] = {
            'passkey': True,
            'name': key.name,
            "id": key.id,
            "platform": key.platform,
            'cross_platform': get_current_platform(request) != key.platform
        }

        return key.user
