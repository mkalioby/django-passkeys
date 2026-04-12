import logging
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def _session_token_backend(user, request):
    from django.contrib.auth import login as auth_login
    if not hasattr(request, 'session'):
        raise ImproperlyConfigured(
            "Session middleware required for session token backend. "
            "Install django-passkeys[drf] for token-based auth."
        )
    auth_login(request, user, backend='passkeys.backend.PasskeyModelBackend')
    return {'token_type': 'session'}


def _drf_token_backend(user, request):
    try:
        from rest_framework.authtoken.models import Token
    except ImportError:
        raise ImproperlyConfigured(
            "rest_framework.authtoken is in INSTALLED_APPS but djangorestframework is not installed"
        )
    token, _ = Token.objects.get_or_create(user=user)
    return {'token_type': 'token', 'token': token.key}


def _jwt_token_backend(user, request):
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
    except ImportError:
        raise ImproperlyConfigured(
            "rest_framework_simplejwt is in INSTALLED_APPS but djangorestframework-simplejwt is not installed"
        )
    refresh = RefreshToken.for_user(user)
    return {
        'token_type': 'jwt',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _load_custom_backend(dotted_path):
    module_path, _, attr = dotted_path.rpartition('.')
    try:
        module = import_module(module_path)
        return getattr(module, attr)
    except (ImportError, AttributeError) as exc:
        raise ImproperlyConfigured(
            f"PASSKEYS_API_TOKEN_BACKEND '{dotted_path}' could not be imported: {exc}"
        )


def get_token_response(user, request):
    """
    Detect the token backend and return auth payload.

    Detection order:
    1. PASSKEYS_API_TOKEN_BACKEND setting (explicit dotted-path to callable)
    2. rest_framework_simplejwt in INSTALLED_APPS
    3. rest_framework.authtoken in INSTALLED_APPS
    4. Fallback: session-based login
    """
    custom = getattr(settings, 'PASSKEYS_API_TOKEN_BACKEND', None)
    if custom:
        backend = _load_custom_backend(custom)
        return backend(user, request)

    installed_apps = settings.INSTALLED_APPS
    if 'rest_framework_simplejwt' in installed_apps:
        return _jwt_token_backend(user, request)
    if 'rest_framework.authtoken' in installed_apps:
        return _drf_token_backend(user, request)

    return _session_token_backend(user, request)
