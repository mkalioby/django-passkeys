from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from .FIDO2 import auth_complete

class PasskeyModelBackend(ModelBackend):
    def authenticate(self, request, username='', password='', **kwargs):

        if username != '' and password != '':
            if request is not None:
                request.session["passkey"] = {'passkey': False}
            return super().authenticate(request, username=username, password=password, **kwargs)

        if request is None:
            if getattr(settings, 'PASSKEYS_ALLOW_EMPTY_RESPONSE', False):
                return None
            raise Exception('request is required for passkeys.backend.PasskeyModelBackend')

        passkeys = request.POST.get('passkeys')
        if passkeys is None:
            if getattr(settings, 'PASSKEYS_ALLOW_NO_PASSKEY_FIELD', False):
                return None
            raise Exception("Can't find 'passkeys' key in request.POST, did you add the hidden input?")
        if passkeys != '':
            return auth_complete(request)
        return None
