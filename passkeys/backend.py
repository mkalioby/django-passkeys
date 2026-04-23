from django.contrib.auth.backends import ModelBackend

from .FIDO2 import auth_complete

class PasskeyModelBackend(ModelBackend):
    def authenticate(self, request, username='', password='', **kwargs):

        if request is None:
            return None

        if username != '' and password != '':
            request.session["passkey"] = {'passkey': False}
            return super().authenticate(request, username=username, password=password, **kwargs)

        passkeys = request.POST.get('passkeys')
        if passkeys is None:
            return None
        if passkeys != '':
            return auth_complete(request)
        return None
