from django.contrib import admin
from django.urls import path, include

from passkey_example.demo import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/login/', views.login_view, name="login"),
    path('auth/logout/', views.logout_view, name="logout"),

    path('', views.home, name='home'),
    path('registered/', views.registered, name='registered'),

    path('passkeys/', include('passkeys.urls')),
]
