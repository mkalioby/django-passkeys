from django import forms
from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import UsernameField, authenticate
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from passkeys.models import UserPasskey

class MyAdminAuthenticationForm(AdminAuthenticationForm):
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


class AppAdminSite(AdminSite):
    site_title = 'Django-Passkeys'
    site_header = 'Django-Passkeys'
    login_template = 'admin_login.html'
    login_form = MyAdminAuthenticationForm

    def get_urls(self):
        urlpatterns = super().get_urls()
        my_urls = [
            path("passkeys/update/", self.admin_view(self.passkeys_update), name="passkeys-update"),
        ]

        return my_urls + urlpatterns

    def passkeys_update(self, request):
        keys = UserPasskey.objects.filter(user=request.user)
        return render(request, 'admin_passkeys.html', {
            'keys': keys, "title": "Your personal passkeys"
        })
