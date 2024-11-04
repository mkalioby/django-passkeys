from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import UsernameField, authenticate, AuthenticationForm
from django.utils.translation import gettext_lazy as _


class MyAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}), required=False)
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        required=False,
    )
    passkeys = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        self.user_cache = authenticate(self.request, username=username, password=password)

        if self.user_cache is None:
            raise self.get_invalid_login_error()
        else:
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class MyAdminAuthenticationForm(MyAuthenticationForm, AdminAuthenticationForm):
    pass
