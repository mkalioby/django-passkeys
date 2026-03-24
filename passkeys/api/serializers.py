try:
    from rest_framework.serializers import (
        ModelSerializer,
        Serializer,
        CharField,
        BooleanField,
        DictField,
    )
except ImportError as exc:
    raise ImportError(
        "djangorestframework is required to use passkeys.api. "
        "Install it with: pip install django-passkeys[drf]"
    ) from exc

from passkeys.models import UserPasskey


class UserPasskeyModelSerializer(ModelSerializer):
    class Meta:
        model = UserPasskey
        fields = ['id', 'name', 'enabled', 'platform', 'added_on', 'last_used']
        read_only_fields = ['id', 'platform', 'added_on', 'last_used']


class UserPasskeyUpdateSerializer(Serializer):
    name = CharField(required=False)
    enabled = BooleanField(required=False)


class RegisterVerifySerializer(Serializer):
    state_token = CharField()
    key_name = CharField(required=False, default='', allow_blank=True)
    credential = DictField()


class AuthenticateOptionsSerializer(Serializer):
    username = CharField(required=False, allow_blank=True, default='')


class AuthenticateVerifySerializer(Serializer):
    state_token = CharField()
    credential = DictField()
