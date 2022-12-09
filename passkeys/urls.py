from django.urls import path
from . import FIDO2,views

app_name = 'passkeys'
urlpatterns = [
    path('auth/begin',FIDO2.auth_begin, name='auth_begin'),
    path('auth/complete',FIDO2.auth_complete, name='auth_complete'),
    path('reg/begin',FIDO2.reg_begin,name = 'reg_begin'),
    path('reg/complete',FIDO2.reg_complete,name = 'reg_complete'),
    path('',views.index, name='home'),
    path('enroll/',views.index, name='enroll',kwargs={'enroll':True}),


    path('del/',views.delKey, name='delKey'),
    path('toggle/',views.toggleKey, name='toggle'),
    ]