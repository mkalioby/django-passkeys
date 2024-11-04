from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from passkeys.models import UserPasskey
from .forms import MyAdminAuthenticationForm


class MyAdminSite(AdminSite):
    site_title = 'Django-Passkeys'
    site_header = 'Django-Passkeys'
    login_form = MyAdminAuthenticationForm

    def get_urls(self):
        urlpatterns = super().get_urls()
        my_urls = [
            path("passkeys/update/", self.admin_view(self.passkeys_update), name="passkeys-update"),
        ]

        return my_urls + urlpatterns

    def passkeys_update(self, request):
        context = {
            **self.each_context(request),
            "title": _("Your personal passkeys"),
            "subtitle": None,
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
            "keys": UserPasskey.objects.filter(user=request.user)
        }

        return render(request, 'admin/passkeys_update.html', context)
