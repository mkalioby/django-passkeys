from django.conf import settings
from django.db import models


class UserPasskey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passkeys')
    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    platform = models.CharField(max_length=255, default='')
    added_on = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, default=None)
    credential_id = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'passkeys_userpasskey'
        verbose_name = 'passkey'
        verbose_name_plural = 'passkeys'
        ordering = ['-added_on']
        indexes = [
            models.Index(fields=['credential_id', 'enabled']),
        ]

    def __str__(self):
        return f"{self.name} ({self.platform})"
