"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views,auth
urlpatterns = [
    path('admin/', admin.site.urls),
    path('passkeys/', include('passkeys.urls')),
    path('api/passkeys/', include('passkeys.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('auth/login/',auth.loginView,name="login"),
    path('auth/logout/',auth.logoutView,name="logout"),
    path('public/', views.public, name='public'),
    path('rest/manage/', views.manage, name = 'rest_manage'),
    path('rest/login/', views.login, name = 'rest_login'),
    path('template/',views.home,name='template'),
    path('',views.choose,name='home'),
    path('registered/',views.registered,name='registered')
]
