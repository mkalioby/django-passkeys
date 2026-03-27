try:
    from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveDestroyAPIView
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework.permissions import IsAuthenticated, AllowAny
    from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotFound
    from rest_framework import status
except ImportError as exc: # pragma: no cover
    raise ImportError(
        "djangorestframework is required to use passkeys.api. "
        "Install it with: pip install django-passkeys[drf]"
    ) from exc

from passkeys.models import UserPasskey
from passkeys.api.serializers import (
    UserPasskeyModelSerializer,
    UserPasskeyUpdateSerializer,
    RegisterVerifySerializer,
    AuthenticateOptionsSerializer,
    AuthenticateVerifySerializer,
)
from passkeys.api.service import (
    reg_begin_service,
    reg_complete_service,
    auth_begin_service,
    auth_complete_service,
    PasskeyStateError,
    PasskeyVerificationError,
    PasskeyNotFoundError,
)
from passkeys.api.token_backends import get_token_response


class UserPasskeyListAPIView(ListAPIView):
    """List all passkeys belonging to the authenticated user."""

    serializer_class = UserPasskeyModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPasskey.objects.filter(user=self.request.user)


class UserPasskeyDetailAPIView(RetrieveDestroyAPIView):
    """
    Retrieve, update, or delete a passkey.

    - GET: Retrieve passkey details.
    - PATCH: Update passkey name or enabled status.
    - DELETE: Remove a passkey. Returns 404 if not owned by the user.
    """

    serializer_class = UserPasskeyModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPasskey.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserPasskeyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(serializer.validated_data.keys()))
        return Response(UserPasskeyModelSerializer(instance).data)


class RegisterOptionsAPIView(APIView):
    """
    Get WebAuthn registration options.

    No request body needed. Returns the public key creation options
    and a signed state token. The state token must be sent back to
    the verify endpoint within 5 minutes.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = reg_begin_service(request.user, request)
        return Response(result)


class RegisterVerifyAPIView(GenericAPIView):
    """
    Verify and save a new passkey credential.

    Accepts the state token from the options step and the credential
    created by the browser's WebAuthn API. Saves the passkey and
    returns the created passkey details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RegisterVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            passkey = reg_complete_service(
                user=request.user,
                state_token=data['state_token'],
                credential=data['credential'],
                key_name=data['key_name'],
                request=request,
            )
        except PasskeyStateError as exc:
            raise ValidationError(str(exc))
        except PasskeyVerificationError as exc:
            raise ValidationError(str(exc))
        return Response(
            UserPasskeyModelSerializer(passkey).data,
            status=status.HTTP_201_CREATED,
        )


class AuthenticateOptionsAPIView(GenericAPIView):
    """
    Get WebAuthn authentication options.

    Optionally accepts a username to narrow allowed credentials.
    If omitted, the browser will show all discoverable passkeys for this domain.

    Returns the public key request options and a signed state token.
    """

    permission_classes = [AllowAny]
    serializer_class = AuthenticateOptionsSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username', '')
        result = auth_begin_service(username or None, request)
        return Response(result)


class AuthenticateVerifyAPIView(GenericAPIView):
    """
    Verify a passkey assertion and authenticate the user.

    Accepts the state token from the options step and the assertion
    from the browser's WebAuthn API. On success, returns the user info
    and an auth token (JWT, DRF Token, or session depending on project config).
    """

    permission_classes = [AllowAny]
    serializer_class = AuthenticateVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = auth_complete_service(
                state_token=data['state_token'],
                credential=data['credential'],
                request=request,
            )
        except PasskeyStateError as exc:
            raise ValidationError(str(exc))
        except PasskeyVerificationError as exc:
            raise AuthenticationFailed(str(exc))
        except PasskeyNotFoundError as exc:
            raise NotFound(str(exc))

        token_data = get_token_response(user, request)
        return Response({
            'user_id': user.pk,
            'username': user.get_username(),
            **token_data,
        })