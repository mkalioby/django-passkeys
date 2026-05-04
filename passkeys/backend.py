from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .FIDO2 import auth_complete

UserModel = get_user_model()
identifier_field = UserModel.USERNAME_FIELD


class PasskeyModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # get actual identifier field (e.g. email) instead of username, to allow for custom user models
        identifier = username or kwargs.get(identifier_field)
        if identifier and password:
            if request is not None:
                request.session["passkey"] = {'passkey': False}

            return super().authenticate(request, username=username, password=password, **kwargs)

        if request is None:
            if getattr(settings, 'PASSKEYS_ALLOW_EMPTY_REQUEST', False):
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
