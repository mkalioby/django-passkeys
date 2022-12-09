from django.contrib.auth.backends import ModelBackend


class PasskeyModelBackend(ModelBackend):
    def authenticate(self, request, username='',password='', **kwargs):
        if request is None:
            raise Exception('request is required for passkeys.backend.PasskeyModelBackend')
        if username!='' and password != '':
            request.session["passkey"]={'passkey':False}
            return super().authenticate(request,username=username,password=password, **kwargs)
        passkeys = request.POST.get('passkeys')
        if not passkeys:
            raise Exception("Can't find '%s' key in request.POST, did you add the hidden input?")
        if len(passkeys)>5:
            from .FIDO2 import auth_complete
            return auth_complete(request)
