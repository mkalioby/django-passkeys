from django.contrib import admin

from passkeys.models import UserPasskey


@admin.register(UserPasskey)
class UserPasskeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')