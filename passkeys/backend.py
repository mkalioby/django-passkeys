from django.contrib.auth.backends import ModelBackend
from .FIDO2 import auth_complete

import logging

LOGGER = logging.getLogger(__name__)


class PasskeyModelBackend(ModelBackend):
    def authenticate(self, request, username='', password='', **kwargs):
        if username != '' and password != '':
            if request is not None:
                request.session["passkey"] = {'passkey': False}

            return super().authenticate(request, username=username, password=password, **kwargs)

        if request is None:
            LOGGER.error(
                "Please pass the request parameter to the authenticate method for this authentication backend to work.")
            return None

        passkeys = request.POST.get('passkeys')
        if passkeys in (None, ''):
            return None

        return auth_complete(request)
