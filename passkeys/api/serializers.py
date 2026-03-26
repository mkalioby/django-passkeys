try:
    from rest_framework.serializers import (
        ModelSerializer,
        Serializer,
        CharField,
        BooleanField,
        DictField,
        IntegerField,
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


# ── Registration ──

class RegisterVerifySerializer(Serializer):
    state_token = CharField()
    key_name = CharField(required=False, default='', allow_blank=True)
    credential = DictField()


class RegisterOptionsResponseSerializer(Serializer):
    options = DictField()
    state_token = CharField()


# ── Authentication ──

class AuthenticateOptionsSerializer(Serializer):
    username = CharField(required=False, allow_blank=True, default='')


class AuthenticateOptionsResponseSerializer(Serializer):
    options = DictField()
    state_token = CharField()


class AuthenticateVerifySerializer(Serializer):
    state_token = CharField()
    credential = DictField()


class AuthenticateVerifyResponseSerializer(Serializer):
    user_id = IntegerField()
    username = CharField()
    token_type = CharField()
    token = CharField(required=False)
    access = CharField(required=False)
    refresh = CharField(required=False)