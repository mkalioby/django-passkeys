from django.contrib import admin

from passkeys.models import UserPasskey


@admin.register(UserPasskey)
class UserPasskeyAdmin(admin.ModelAdmin):
    search_fields = ('user__last_name', 'user__first_name', 'user__email', 'platform')
    list_display = ('user', 'name', 'platform', 'enabled', 'added_on', 'last_used')
    list_filter = ('enabled', 'added_on', 'last_used')

    def has_change_permission(self, request, obj=None):
        return False