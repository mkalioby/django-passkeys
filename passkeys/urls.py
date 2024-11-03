from django.urls import path
from . import util, views

app_name = 'passkeys'

urlpatterns = [
    path('auth/begin/', views.auth_begin, name='auth_begin'),

    path('reg/begin/', views.reg_begin, name='reg_begin'),
    path('reg/complete/', views.reg_complete, name='reg_complete'),

    path('', views.index, name='home'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('toggle/<int:pk>/', views.toggle, name='toggle'),
]
