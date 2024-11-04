from django.contrib import admin
from django.urls import path, include

from passkey_example import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/login/', views.login_view, name="login"),
    path('auth/logout/', views.logout_view, name="logout"),

    path('passkeys/', include('passkeys.urls')),

    path('', views.home, name='home'),

]
