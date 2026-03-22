from django.contrib import admin
from django.urls import path, re_path, include

from . import views, auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('passkeys/', include('passkeys.urls')),
    path('auth/login', auth.login_view, name="login"),
    path('auth/logout', auth.logout_view, name="logout"),
    re_path('^$', views.home, name='home'),
    path('registered/', views.registered, name='registered'),
]
