from django.urls import path

from . import webauthn, views

app_name = 'passkeys'
urlpatterns = [
    path('auth/begin', webauthn.auth_begin, name='auth_begin'),
    path('auth/complete', webauthn.auth_complete, name='auth_complete'),
    path('reg/begin', webauthn.reg_begin, name='reg_begin'),
    path('reg/complete', webauthn.reg_complete, name='reg_complete'),
    path('', views.index, name='home'),
    path('enroll/', views.index, name='enroll', kwargs={'enroll': True}),
    path('del/', views.del_key, name='del_key'),
    path('toggle/', views.toggle_key, name='toggle'),
]
