from django.contrib.auth import get_user_model
from django.db import models


class UserPasskey(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    enabled= models.BooleanField(default=True)
    platform = models.CharField(max_length=255,default='')
    added_on = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True,default=None)
    credential_id = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=255, null=False)