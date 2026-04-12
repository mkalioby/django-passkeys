from django.urls import path

from passkeys.api.views import (
    UserPasskeyListAPIView,
    UserPasskeyDetailAPIView,
    RegisterOptionsAPIView,
    RegisterVerifyAPIView,
    AuthenticateOptionsAPIView,
    AuthenticateVerifyAPIView,
)

app_name = 'passkeys_api'

urlpatterns = [
    path('', UserPasskeyListAPIView.as_view(), name='list'),
    path('<int:pk>', UserPasskeyDetailAPIView.as_view(), name='detail'),
    path('register/options', RegisterOptionsAPIView.as_view(), name='register_options'),
    path('register/verify', RegisterVerifyAPIView.as_view(), name='register_verify'),
    path('authenticate/options', AuthenticateOptionsAPIView.as_view(), name='authenticate_options'),
    path('authenticate/verify', AuthenticateVerifyAPIView.as_view(), name='authenticate_verify'),
]
